import pandas as pd
from datetime import datetime
from web3 import Web3
from .base import BaseProcessor
from ..constants.uniswap import (
    UNISWAP_V3_FACTORY,
    UNISWAP_V3_FACTORY_ABI,
    UNISWAP_V3_POOL_ABI,
    SUPPORTED_STABLECOINS,
    WETH_ADDRESS
)
from ..exceptions import PriceDataError

class UniswapV3Processor(BaseProcessor):
    async def fetch_data(self, contract_address: str, timeframe: str, interval_days: int) -> pd.DataFrame:
        """Fetch price data from Uniswap V3"""
        try:
            factory = self.w3.eth.contract(
                address=Web3.to_checksum_address(UNISWAP_V3_FACTORY),
                abi=UNISWAP_V3_FACTORY_ABI
            )
            
            pools = await self._find_pools(factory, contract_address)
            if not pools:
                return pd.DataFrame()
                
            df = await self._process_pools(pools, contract_address, interval_days)
            return self._process_price_data(df, timeframe)
            
        except Exception as e:
            print(f"[V3] ❌ Error: {str(e)}")
            return pd.DataFrame()

    async def _process_pools(self, pools: list[dict], contract_address: str, interval_days: int) -> pd.DataFrame:
        """Process pools and return price data"""
        all_prices = []
        timestamps_for_weth = set()
        swap_data = []
        
        # Calculate block range
        end_block = self.w3.eth.block_number
        blocks_per_day = 7200
        start_block = max(0, end_block - (interval_days * blocks_per_day))
        
        swap_event_signature = Web3.keccak(
            text="Swap(address,address,int256,int256,uint160,uint128,int24)"
        ).hex()
        
        # First pass: collect all swap events and timestamps
        for pool_info in pools:
            try:
                pool_address = pool_info['address']
                base_token = pool_info['base']
                is_weth_pool = base_token == 'WETH'
                
                if not is_weth_pool:
                    continue
                
                pool = self.w3.eth.contract(
                    address=Web3.to_checksum_address(pool_address),
                    abi=UNISWAP_V3_POOL_ABI
                )
                
                token0 = pool.functions.token0().call()
                token1 = pool.functions.token1().call()
                decimals0 = self.w3.eth.contract(address=token0, abi=[{"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}]).functions.decimals().call()
                decimals1 = self.w3.eth.contract(address=token1, abi=[{"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}]).functions.decimals().call()
                is_token0 = Web3.to_checksum_address(contract_address) == token0
                
                logs = self.w3.eth.get_logs({
                    'address': Web3.to_checksum_address(pool_address),
                    'topics': [swap_event_signature],
                    'fromBlock': start_block,
                    'toBlock': end_block
                })
                
                print(f"[V3] 📊 Found {len(logs)} swap events in WETH pool")
                
                for log in logs:
                    block = self.w3.eth.get_block(log['blockNumber'])
                    timestamps_for_weth.add(block['timestamp'])
                    
                    decoded_log = pool.events.Swap().process_log(log)
                    swap_data.append({
                        'timestamp': block['timestamp'],
                        'amount0': decoded_log['args']['amount0'],
                        'amount1': decoded_log['args']['amount1'],
                        'decimals0': decimals0,
                        'decimals1': decimals1,
                        'is_token0': is_token0
                    })
                    
            except Exception as e:
                print(f"[V3] ⚠️ Error processing pool: {str(e)}")
                continue
        
        if not timestamps_for_weth:
            return pd.DataFrame()
            
        # Get WETH prices from DefiLlama
        weth_prices = await self.defillama_processor.get_historical_weth_prices(list(timestamps_for_weth))
        
        # Calculate final prices using WETH data
        for swap in swap_data:
            try:
                timestamp = str(swap['timestamp'])
                weth_price = weth_prices.get(timestamp)
                
                if not weth_price:
                    continue
                    
                if swap['is_token0']:
                    raw_price = abs(swap['amount1']) / (10**swap['decimals1']) / (abs(swap['amount0']) / (10**swap['decimals0']))
                else:
                    raw_price = abs(swap['amount0']) / (10**swap['decimals0']) / (abs(swap['amount1']) / (10**swap['decimals1']))
                
                price = raw_price * weth_price
                
                all_prices.append({
                    'timestamp': datetime.fromtimestamp(int(timestamp)),
                    'price': float(price)
                })
                
            except Exception as e:
                print(f"[V3] ⚠️ Error calculating price: {str(e)}")
                continue
                
        return pd.DataFrame(all_prices)

    async def _find_pools(self, factory, contract_address: str) -> list[dict]:
        """Find all available pools for the token"""
        print("[V3] 🔍 Searching for Uniswap V3 pools...")
        pools = []

        # Check stablecoin pairs first
        print("[V3] 🔍 Checking stablecoin pairs first...")
        for addr, (symbol, decimals, priority) in SUPPORTED_STABLECOINS.items():
            for fee in [100, 500, 3000, 10000]:
                try:
                    pool_address = factory.functions.getPool(
                        Web3.to_checksum_address(contract_address),
                        Web3.to_checksum_address(addr),
                        fee
                    ).call()
                    
                    if pool_address != "0x0000000000000000000000000000000000000000":
                        pool = self.w3.eth.contract(
                            address=Web3.to_checksum_address(pool_address),
                            abi=UNISWAP_V3_POOL_ABI
                        )
                        liquidity = pool.functions.liquidity().call()
                        
                        pools.append({
                            'address': pool_address,
                            'base': symbol,
                            'base_address': addr,
                            'fee': fee,
                            'decimals': decimals,
                            'priority': priority,
                            'liquidity': liquidity
                        })
                        print(f"[V3] ✅ Found {symbol} pool: {pool_address} (fee: {fee/10000}%)")
                except Exception as e:
                    print(f"[V3] ⚠️ Error checking {symbol} pool with fee {fee/10000}%: {str(e)}")
                    continue

        # Check WETH pair if no stablecoin pairs found
        if not pools:
            print("[V3] ℹ️ No stablecoin pairs found, checking WETH pairs...")
            try:
                for fee in [500, 3000, 10000]:
                    pool_address = factory.functions.getPool(
                        Web3.to_checksum_address(contract_address),
                        Web3.to_checksum_address(WETH_ADDRESS),
                        fee
                    ).call()
                    
                    if pool_address != "0x0000000000000000000000000000000000000000":
                        pool = self.w3.eth.contract(
                            address=Web3.to_checksum_address(pool_address),
                            abi=UNISWAP_V3_POOL_ABI
                        )
                        liquidity = pool.functions.liquidity().call()
                        
                        pools.append({
                            'address': pool_address,
                            'base': 'WETH',
                            'base_address': WETH_ADDRESS,
                            'fee': fee,
                            'decimals': 18,
                            'priority': 3,
                            'liquidity': liquidity
                        })
                        print(f"[V3] ✅ Found WETH pool: {pool_address} (fee: {fee/10000}%)")
            except Exception as e:
                print(f"[V3] ⚠️ Error checking WETH pools: {str(e)}")

        return sorted(pools, key=lambda x: (x['priority'], -x['liquidity'])) 