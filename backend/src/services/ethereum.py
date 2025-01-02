from web3 import Web3
from typing import Dict
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from fastapi import HTTPException
from ..config import ETHEREUM_RPC_ENDPOINTS
import asyncio
import json

# Add Uniswap constants
UNISWAP_V2_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
UNISWAP_V3_FACTORY = "0x1F98431c8aD98523631AE4a59f267346ea31F984"
WETH_ADDRESS = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
USDT_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

# Add CoinGecko constants
COINGECKO_API_KEY = "CG-bLvBUpsF1FbTMrL9RVAaHZWu"
COINGECKO_PRO_API = "https://pro-api.coingecko.com/api/v3"

# Full Uniswap V2 Pair ABI
UNISWAP_V2_PAIR_ABI = json.loads('''[
    {
        "constant": true,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"name": "_reserve0", "type": "uint112"},
            {"name": "_reserve1", "type": "uint112"},
            {"name": "_blockTimestampLast", "type": "uint32"}
        ],
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "token0",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "token1",
        "outputs": [{"name": "", "type": "address"}],
        "type": "function"
    }
]''')

class EthereumService:
    def __init__(self):
        # Initialize Web3 connection
        for rpc_url in ETHEREUM_RPC_ENDPOINTS:
            if not rpc_url.startswith('http'):
                continue
            try:
                self.w3 = Web3(Web3.HTTPProvider(rpc_url))
                if self.w3.is_connected():
                    print(f"Connected to Ethereum node: {rpc_url}")
                    break
            except Exception as e:
                print(f"Failed to connect to {rpc_url}: {str(e)}")
                continue
        
        if not hasattr(self, 'w3') or not self.w3.is_connected():
            raise Exception("Failed to connect to any Ethereum HTTP RPC endpoint")
            
        # Initialize price cache
        self.eth_price_cache = {}

    async def validate_token(self, contract_address: str) -> Dict:
        """Validates token contract and returns basic token information"""
        try:
            # First verify contract exists on-chain
            contract_code = self.w3.eth.get_code(Web3.to_checksum_address(contract_address))
            if contract_code == '0x' or contract_code == b'':
                raise ValueError("Contract does not exist on-chain")

            # Try to get ERC20 basic info directly from the contract
            try:
                contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(contract_address),
                    abi=[
                        {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                        {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                        {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
                    ]
                )
                
                name = contract.functions.name().call()
                symbol = contract.functions.symbol().call()
                decimals = contract.functions.decimals().call()
                
                token_info = {
                    "address": contract_address,
                    "name": name,
                    "symbol": symbol.upper(),
                    "decimals": decimals,
                    "is_valid": True
                }
                
                # Try CoinGecko as additional data source, but don't fail if unavailable
                try:
                    async with aiohttp.ClientSession() as session:
                        url = f"{COINGECKO_PRO_API}/coins/ethereum/contract/{contract_address}"
                        headers = {
                            "x-cg-pro-api-key": COINGECKO_API_KEY
                        }
                        async with session.get(url, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                token_info.update({
                                    "coingecko_id": data.get('id'),
                                    "market_cap": data.get('market_data', {}).get('market_cap', {}).get('usd'),
                                    "total_supply": data.get('market_data', {}).get('total_supply')
                                })
                except Exception as e:
                    print(f"[Token] ⚠️ CoinGecko API error: {str(e)}")
                    pass  # Ignore CoinGecko errors
                    
                return token_info

            except Exception as contract_error:
                raise ValueError(f"Invalid ERC20 contract: {str(contract_error)}")

        except Exception as e:
            raise ValueError(f"Invalid token contract: {str(e)}")

    async def fetch_price_data(self, contract_address: str, timeframe: str, interval_days: int) -> pd.DataFrame:
        """Fetch historical price data from CoinGecko Pro API"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=interval_days)
        
        headers = {
            "x-cg-pro-api-key": COINGECKO_API_KEY
        }
        
        async with aiohttp.ClientSession() as session:
            url = f"{COINGECKO_PRO_API}/coins/ethereum/contract/{contract_address}/market_chart/range"
            params = {
                "vs_currency": "usd",
                "from": int(start_time.timestamp()),
                "to": int(end_time.timestamp())
            }
            
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise HTTPException(
                        status_code=response.status, 
                        detail=f"CoinGecko API error: {error_data.get('error', 'Unknown error')}"
                    )
                
                data = await response.json()
                
                # Convert to DataFrame
                df = pd.DataFrame(data['prices'], columns=['timestamp', 'close'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                
                # Resample to desired timeframe
                df.set_index('timestamp', inplace=True)
                df = df.resample(timeframe).agg({
                    'close': 'last'
                }).dropna()
                
                # Add OHLC data (you should replace this with actual OHLC data from your API)
                df['open'] = df['close'].shift(1)
                df['high'] = df['close'] * 1.001  # Placeholder
                df['low'] = df['close'] * 0.999   # Placeholder
                df['volume'] = 0                   # Placeholder
                
                return df

    async def get_v2_historical_prices(self, pair_address: str, token_address: str, timeframe: str, interval_days: int) -> list:
        """Fetch historical prices from Uniswap V2 pair with better error handling"""
        try:
            pair_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(pair_address),
                abi=UNISWAP_V2_PAIR_ABI
            )
            
            # Get token positions and decimals
            token0 = pair_contract.functions.token0().call()
            token1 = pair_contract.functions.token1().call()
            is_token0 = Web3.to_checksum_address(token_address) == token0
            
            # Get decimals for price adjustment
            decimals0 = self.w3.eth.contract(
                address=token0,
                abi=[{"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}]
            ).functions.decimals().call()
            decimals1 = self.w3.eth.contract(
                address=token1,
                abi=[{"constant":True,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"type":"function"}]
            ).functions.decimals().call()
            
            decimals_ratio = 10 ** (decimals1 - decimals0 if is_token0 else decimals0 - decimals1)
            
            # Calculate block range with more reasonable sampling
            blocks_per_hour = 300  # ~300 blocks per hour
            current_block = self.w3.eth.block_number
            total_blocks = interval_days * 24 * blocks_per_hour
            block_step = max(300, total_blocks // 1000)  # Sample at most 1000 points
            start_block = current_block - total_blocks
            
            print(f"[V2] 📊 Fetching prices from block {start_block} to {current_block}")
            print(f"[V2] 📊 Sampling every {block_step} blocks")
            
            prices = []
            last_progress = -1
            
            for block_num in range(start_block, current_block, block_step):
                try:
                    progress = int(((block_num - start_block) / total_blocks) * 100)
                    if progress > last_progress and progress % 10 == 0:
                        print(f"[V2] ⏳ Progress: {progress}% - Block: {block_num}")
                        last_progress = progress
                    
                    try:
                        reserves = pair_contract.functions.getReserves().call(block_identifier=block_num)
                        reserve0, reserve1 = reserves[0], reserves[1]
                    except Exception as e:
                        print(f"[V2] ⚠️ Block {block_num}: {str(e)}")
                        continue
                    
                    if reserve0 == 0 or reserve1 == 0:
                        continue
                    
                    price = (reserve1 / reserve0) * decimals_ratio if is_token0 else (reserve0 / reserve1) / decimals_ratio
                    
                    block = self.w3.eth.get_block(block_num)
                    timestamp = datetime.fromtimestamp(block['timestamp'])
                    
                    prices.append({
                        'timestamp': timestamp,
                        'price': float(price)
                    })
                    
                except Exception as e:
                    print(f"[V2] ⚠️ Error at block {block_num}: {str(e)}")
                    continue
                
                await asyncio.sleep(0.1)  # Rate limiting
            
            print(f"[V2] ✅ Collected {len(prices)} price points")
            return prices
            
        except Exception as e:
            print(f"[V2] ❌ Failed to fetch V2 prices: {str(e)}")
            return []

    async def get_uniswap_v2_pair(self, token_address: str) -> str:
        """Get Uniswap V2 pair address for token with common base pairs"""
        try:
            factory = self.w3.eth.contract(
                address=Web3.to_checksum_address(UNISWAP_V2_FACTORY),
                abi=[{
                    "constant": True,
                    "inputs": [
                        {"name": "tokenA", "type": "address"},
                        {"name": "tokenB", "type": "address"}
                    ],
                    "name": "getPair",
                    "outputs": [{"name": "pair", "type": "address"}],
                    "type": "function"
                }]
            )
            
            # Base pairs in priority order
            base_pairs = [
                (USDC_ADDRESS, "USDC"),
                (USDT_ADDRESS, "USDT"),
                (WETH_ADDRESS, "WETH")
            ]
            
            for base_token, base_name in base_pairs:
                try:
                    pair_address = factory.functions.getPair(
                        Web3.to_checksum_address(token_address),
                        Web3.to_checksum_address(base_token)
                    ).call()
                    
                    if pair_address != "0x0000000000000000000000000000000000000000":
                        print(f"[V2] ✅ Found {base_name} pair: {pair_address}")
                        return pair_address
                        
                except Exception as e:
                    print(f"[V2] ⚠️ Error checking {base_name} pair: {str(e)}")
                    continue
                    
            print("[V2] ❌ No pairs found with USDC, USDT, or WETH")
            return None
                
        except Exception as e:
            print(f"[V2] ❌ Error getting V2 pair: {str(e)}")
            return None

    async def supports_interface(self, contract_address: str, interface_id: str) -> bool:
        """Check if contract supports ERC165 interface"""
        try:
            # ERC165 interface check ABI
            erc165_abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "interfaceId", "type": "bytes4"}],
                    "name": "supportsInterface",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                }
            ]
            
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(contract_address),
                abi=erc165_abi
            )
            
            try:
                # Try ERC165 interface check first
                return contract.functions.supportsInterface(interface_id).call()
            except Exception:
                # If ERC165 check fails, try basic ERC20 function calls
                erc20_contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(contract_address),
                    abi=[
                        {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
                        {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"}
                    ]
                )
                
                # Try to call basic ERC20 functions
                _ = erc20_contract.functions.decimals().call()
                _ = erc20_contract.functions.symbol().call()
                return True  # If both calls succeed, it's likely an ERC20 token
                
        except Exception as e:
            print(f"[Token] ⚠️ Interface check failed: {str(e)}")
            return False

    async def get_contract_code(self, contract_address: str) -> bytes:
        """Get contract bytecode from the blockchain"""
        try:
            return self.w3.eth.get_code(Web3.to_checksum_address(contract_address))
        except Exception as e:
            print(f"[RPC] ⚠️ Error getting contract code: {str(e)}")
            raise

    async def get_eth_price_at_time(self, block_number: int, timestamp: int) -> float:
        """Get ETH price at a specific block/timestamp"""
        # Check cache first
        if block_number in self.eth_price_cache:
            return self.eth_price_cache[block_number]
            
        try:
            # Use USDC/WETH pool as price oracle
            pool = self.w3.eth.contract(
                address=Web3.to_checksum_address("0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8"),  # USDC/WETH 0.3% pool
                abi=[{
                    "inputs": [],
                    "name": "slot0",
                    "outputs": [
                        {"name": "sqrtPriceX96", "type": "uint160"},
                        {"name": "tick", "type": "int24"},
                        {"name": "observationIndex", "type": "uint16"},
                        {"name": "observationCardinality", "type": "uint16"},
                        {"name": "observationCardinalityNext", "type": "uint16"},
                        {"name": "feeProtocol", "type": "uint8"},
                        {"name": "unlocked", "type": "bool"}
                    ],
                    "stateMutability": "view",
                    "type": "function"
                }]
            )
            
            # Get price from sqrt price
            slot0 = pool.functions.slot0().call(block_identifier=block_number)
            sqrt_price_x96 = slot0[0]
            eth_price = (sqrt_price_x96 * sqrt_price_x96 * (10**12)) >> (96 * 2)
            eth_price = eth_price / 1e6  # Convert to USD
            
            # Cache the result
            self.eth_price_cache[block_number] = eth_price
            return eth_price
            
        except Exception as e:
            print(f"[Price] ⚠️ Error getting ETH price: {str(e)}")
            # Return a fallback price if oracle fails
            return 2000.0  # Fallback price