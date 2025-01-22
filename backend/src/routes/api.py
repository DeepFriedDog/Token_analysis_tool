from fastapi import APIRouter, HTTPException
from decimal import Decimal, InvalidOperation, ROUND_DOWN
import pandas as pd
from ..services.price import PriceService
from ..services.dca import DCAStrategyFacade
from ..services.sentiment import SentimentAnalyzer
from ..models.requests import TokenAnalysisRequest, SentimentAnalysisRequest
from pydantic import BaseModel

router = APIRouter()
price_service = PriceService()
sentiment_analyzer = SentimentAnalyzer()

@router.post("/api/analyze")
async def analyze_token(request: TokenAnalysisRequest):
    try:
        print(f"\n[API] 📊 Analyzing token: {request.contract_address}")
        print(f"[API] ⚙️ Parameters: timeframe={request.timeframe}, interval_days={request.interval_days}")
        
        price_data = await price_service.get_price_data(
            contract_address=request.contract_address,
            timeframe=request.timeframe,
            interval_days=request.interval_days
        )
        
        if not price_data or 'priceData' not in price_data:
            return {
                "priceData": {
                    "price_history": [],
                    "current_price": "0"
                },
                "technical_analysis": {
                    "support_levels": [],
                    "resistance_levels": [],
                    "rsi": "50.0",
                    "volatility": "0.0",
                    "advanced_indicators": {
                        "macd": None,
                        "bollinger_bands": None,
                        "rsi": 50.0
                    }
                },
                "dca_strategy": None
            }
        
        df = pd.DataFrame([
            {
                'timestamp': pd.to_datetime(p['timestamp']),
                'close': Decimal(str(p['value'])),
                'high': Decimal(str(p.get('formatted', {}).get('high', p['value']))),
                'low': Decimal(str(p.get('formatted', {}).get('low', p['value'])))
            }
            for p in price_data['priceData']['price_history']
        ]).set_index('timestamp')
        
        technical_analysis = price_data['technical_analysis']
        
        strategy_facade = DCAStrategyFacade(
            price_data=df,
            investment_amount=Decimal(str(request.investment_amount)),
            risk_tolerance=Decimal('0.5')
        )
        
        analysis_result = strategy_facade.get_analysis_result(
            support_levels=technical_analysis['support_levels'],
            resistance_levels=technical_analysis['resistance_levels'],
            fibonacci_levels=technical_analysis.get('fibonacci_levels', [])
        )
        
        return {
            "priceData": {
                "price_history": [
                    {
                        'timestamp': p['timestamp'],
                        'price': p['value'],
                        'high': p['formatted']['high'],
                        'low': p['formatted']['low']
                    }
                    for p in price_data['priceData']['price_history']
                ],
                "current_price": price_data['priceData']['price_history'][-1]['value'] if price_data['priceData']['price_history'] else "0"
            },
            "technical_analysis": technical_analysis,
            "dca_strategy": analysis_result
        }
        
    except Exception as e:
        print(f"[API] ❌ Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class SentimentAnalysisRequest(BaseModel):
    telegram_channel: str
    interval_days: int
    advanced_analysis: bool = False

@router.post("/api/analyze-sentiment")
async def analyze_sentiment(request: SentimentAnalysisRequest):
    try:
        sentiment_result = await sentiment_analyzer.analyze_channel(
            channel=request.telegram_channel,
            days=request.interval_days,
            advanced_mode=request.advanced_analysis
        )
        
        return sentiment_result
    except Exception as e:
        print(f"[API] ❌ Sentiment analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Sentiment analysis failed: {str(e)}"
        ) 