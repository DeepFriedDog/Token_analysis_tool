import json
from ...ethereum import (
    USDC_ADDRESS,
    USDT_ADDRESS,
    WETH_ADDRESS,
    UNISWAP_V3_FACTORY
)

# Supported stablecoins configuration
SUPPORTED_STABLECOINS = {
    USDC_ADDRESS: ("USDC", 6, 1),  # Highest priority
    USDT_ADDRESS: ("USDT", 6, 1),  # Equal priority with USDC
    "0x6B175474E89094C44Da98b954EedeAC495271d0F": ("DAI", 18, 2),  # Medium priority
    "0x4Fabb145d64652a948d72533023f6E7A623C7C53": ("BUSD", 18, 2)  # Medium priority
}

# Export UNISWAP_V3_FACTORY
__all__ = ['UNISWAP_V3_FACTORY', 'UNISWAP_V3_FACTORY_ABI', 'UNISWAP_V3_POOL_ABI', 'SUPPORTED_STABLECOINS', 'WETH_ADDRESS']

# ABIs
UNISWAP_V3_FACTORY_ABI = json.loads('''[
    {"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"}],"name":"getPool","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}
]''')

UNISWAP_V3_POOL_ABI = [{
    "constant": True,
    "inputs": [],
    "name": "token0",
    "outputs": [{"name": "", "type": "address"}],
    "type": "function"
}, {
    "constant": True,
    "inputs": [],
    "name": "token1",
    "outputs": [{"name": "", "type": "address"}],
    "type": "function"
}, {
    "constant": True,
    "inputs": [],
    "name": "fee",
    "outputs": [{"name": "", "type": "uint24"}],
    "type": "function"
}, {
    "constant": True,
    "inputs": [],
    "name": "liquidity",
    "outputs": [{"name": "", "type": "uint128"}],
    "type": "function"
}, {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "name": "sender", "type": "address"},
        {"indexed": True, "name": "recipient", "type": "address"},
        {"indexed": False, "name": "amount0", "type": "int256"},
        {"indexed": False, "name": "amount1", "type": "int256"},
        {"indexed": False, "name": "sqrtPriceX96", "type": "uint160"},
        {"indexed": False, "name": "liquidity", "type": "uint128"},
        {"indexed": False, "name": "tick", "type": "int24"}
    ],
    "name": "Swap",
    "type": "event"
}]