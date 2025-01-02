# Token Analysis Tool

## Overview

A sophisticated DCA (Dollar-Cost Averaging) analysis tool for Ethereum tokens that combines technical analysis, historical data, and risk assessment to provide data-driven investment strategies.

## Core Features

### 1. Technical Analysis
- **Support & Resistance Detection**
  - Uses historical price action and volume profiles
  - Identifies key price levels where buying/selling pressure is significant
  - Strength scoring based on level clustering and historical validation
  - Real-time distance calculation from current price (highlighting levels within 5%)

- **Trend Analysis**
  - Multiple timeframe analysis (1h, 4h, 1d)
  - Moving averages (20 and 50-day)
  - RSI (Relative Strength Index) for momentum
  - Volatility calculations for risk assessment

### 2. DCA Strategy Generation

- **Entry Points Calculation**
  - Support level-based entries with strength weighting
  - Volatility-based dynamic entries
  - Position sizing correlated with:
    - Level strength
    - Distance from current price
    - Overall market volatility
    - Risk tolerance settings

- **Investment Distribution**
  - Weighted position sizing based on technical strength
  - Risk-adjusted allocation
  - Dynamic rebalancing suggestions

### 3. Risk Assessment

- **Multi-factor Risk Scoring**
  - RSI-based market momentum (40% weight)
  - Volatility impact (40% weight)
  - Support/Resistance structure (20% weight)
  - Key risk indicators and mitigations

## Technical Implementation

### Price Data Processing
- Primary Source: DefiLlama API
- Features:
  - High precision price data (8 decimal places)
  - Automatic rate limit handling
  - Error recovery and data validation
  - Historical data aggregation

### Analysis Methodology

1. **Support/Resistance Detection**
   - Price action analysis
   - Volume profile correlation
   - Level strength calculation based on historical touches
   - Clustering analysis for level confirmation

2. **Entry Point Generation**
   - Support level validation
   - Moving average crossovers
   - Volatility-based entry calculation
   - Position size optimization

3. **Risk Calculation**
   - Technical indicator aggregation
   - Market structure analysis
   - Volatility impact assessment
   - Dynamic risk scoring

## Data Sources

1. **Price Data**
   - Primary: DefiLlama API
   - Features:
     - Real-time price updates
     - Historical data up to 365 days
     - High precision (8 decimals)
     - Multiple timeframe support

2. **Technical Indicators**
   - Calculated using:
     - Price action
     - Volume profiles
     - Moving averages
     - Momentum indicators

## Practical Applications

1. **DCA Strategy Optimization**
   - Optimal entry point identification
   - Position size recommendations
   - Risk-adjusted investment distribution
   - Dynamic strategy adjustment

2. **Risk Management**
   - Real-time risk assessment
   - Market condition monitoring
   - Position size optimization
   - Stop-loss recommendations

3. **Investment Planning**
   - Long-term accumulation strategies
   - Risk-adjusted position sizing
   - Market timing optimization
   - Portfolio rebalancing guidance

## Rate Limits and Data Quality

- DefiLlama API:
  - Rate limit: 10-200 requests per minute
  - Automatic rate limiting implemented
  - Error handling and retry logic
  - Data validation and cleaning

## Technical Requirements

### Backend Dependencies
- Python FastAPI
- pandas for data analysis
- numpy/scipy for technical calculations
- Web3.py for Ethereum interaction

### Frontend Stack
- Next.js/React
- TypeScript
- TailwindCSS
- TradingView charts

## Installation and Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/token-analysis-tool.git
cd token-analysis-tool
```

2. Install TA-Lib (required for technical analysis):

Windows:
- Download ta-lib-0.4.0-msvc.zip from https://ta-lib.org/hdr_dw.html
- Extract to C:\ta-lib
- Add C:\ta-lib\lib to your system's PATH environment variable
- Alternative: Download pre-built wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

Linux:
```bash
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
```

3. Create and activate virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python -m venv venv
source venv/bin/activate
```

4. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

5. Install frontend dependencies
```bash
cd frontend
npm install
```

6. Start the backend server:
```bash
cd backend
uvicorn src.main:app --reload
# Server will run on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

7. Start the frontend development server:
```bash
cd frontend
npm run dev
# Frontend will run on http://localhost:3000
```

## API Documentation

### Token Analysis Endpoint

#### Request Body
```json
{
  "contract_address": "string",    // Ethereum token contract address
  "timeframe": "string",          // "15m", "1h", "4h", "1d"
  "interval_days": integer,       // Analysis period (default: 30)
  "investment_amount": float      // Amount to invest (default: 100.0)
}
```

#### Response
```json
{
  "token_info": {
    "address": "string",
    "name": "string",
    "symbol": "string",
    "decimals": integer,
    "is_valid": boolean
  },
  "technical_analysis": {
    "support_levels": [float],
    "resistance_levels": [float],
    "fibonacci_levels": [
      {
        "level": float,
        "price": float,
        "type": string
      }
    ],
    "rsi": float,
    "volatility": float
  },
  "dca_strategy": {
    "entry_points": [
      {
        "price": float,
        "percentage": float,
        "timestamp": string
      }
    ],
    "exit_points": [
      {
        "price": float,
        "percentage": float,
        "type": string
      }
    ],
    "risk_score": float,
    "expected_return": float,
    "investment_distribution": [
      {
        "amount": float,
        "timestamp": string,
        "price_target": float
      }
    ]
  },
  "backtest_results": {
    "historical_performance": float,
    "win_rate": float,
    "average_return": float,
    "max_drawdown": float,
    "risk_adjusted_return": float
  }
}
```

### Error Responses

```json
{
  "error": "string",
  "detail": "string",
  "status_code": integer
}
```

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

Note: This project uses free public APIs for Ethereum RPC and price data. The endpoints are configured in `backend/src/config.py`.

Public APIs used:
- Ethereum RPC: Ankr, Cloudflare, Public RPC
- Price Data: DefiLlama API