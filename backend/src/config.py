# Ethereum RPC endpoints (free)
ETHEREUM_RPC_ENDPOINTS = [
    "https://rpc.ankr.com/eth",
    "https://cloudflare-eth.com",
    "https://eth.public-rpc.com"
]

# The Graph API endpoints (free)
UNISWAP_V3_SUBGRAPH = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
UNISWAP_V2_SUBGRAPH = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"

# CoinGecko API (free)
COINGECKO_API = "https://api.coingecko.com/api/v3"

# Rate limits (requests per minute)
RATE_LIMITS = {
    "coingecko": 50,
    "thegraph": 25
} 