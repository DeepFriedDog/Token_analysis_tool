from fastapi import APIRouter, HTTPException
from decimal import Decimal, InvalidOperation, ROUND_DOWN
import pandas as pd
from ..services.price import PriceService
from ..services.dca import DCAStrategyFacade
from ..services.sentiment import SentimentAnalyzer
from ..models.requests import TokenAnalysisRequest, SentimentAnalysisRequest

router = APIRouter()
price_service = PriceService()
sentiment_analyzer = SentimentAnalyzer()

@router.post("/api/analyze")
async def analyze_token(request: TokenAnalysisRequest):
    try:
        print(f"\n[API] 📊 Analyzing token: {request.contract_address}")
        print(f"[API] ⚙️ Parameters: timeframe={request.timeframe}, interval_days={request.interval_days}")
        
        df = await price_service.fetch_price_data(
            contract_address=request.contract_address,
            timeframe=request.timeframe,
            interval_days=request.interval_days
        )
        
        if df.empty:
            return {
                "priceData": [],
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
        
        try:
            # Calculate technical indicators
            technical_analysis = price_service.calculate_technical_indicators(df)
            
            # Create strategy facade
            strategy_facade = DCAStrategyFacade(
                price_data=df,
                investment_amount=Decimal(str(request.investment_amount)),
                risk_tolerance=Decimal('0.5')
            )
            
            # Format price data for frontend
            price_data = df.reset_index()
            formatted_price_data = [
                {
                    "timestamp": record["timestamp"].isoformat() if isinstance(record["timestamp"], pd.Timestamp) else str(record["timestamp"]),
                    "close": str(Decimal(str(record["close"])).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN))
                }
                for record in price_data.to_dict('records')
            ]
            
            # Get analysis results
            analysis_result = strategy_facade.get_analysis_result(
                support_levels=technical_analysis['support_levels'],
                resistance_levels=technical_analysis['resistance_levels'],
                fibonacci_levels=technical_analysis['fibonacci_levels']
            )
            
            return {
                "priceData": formatted_price_data,
                "technical_analysis": technical_analysis,
                "dca_strategy": analysis_result
            }
            
        except (InvalidOperation, ValueError, TypeError) as e:
            print(f"[API] ❌ Calculation error: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=f"Error in calculations: {str(e)}"
            )
            
    except Exception as e:
        print(f"[API] ❌ Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/api/analyze-sentiment")
async def analyze_sentiment(request: SentimentAnalysisRequest):
    try:
        sentiment_result = await sentiment_analyzer.analyze_channel(
            channel=request.telegram_channel,
            days=request.interval_days
        )
        
        return sentiment_result
    except Exception as e:
        print(f"[API] ❌ Sentiment analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Sentiment analysis failed: {str(e)}"
        ) 