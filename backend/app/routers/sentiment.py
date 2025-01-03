from fastapi import APIRouter, HTTPException
from backend.services.sentiment_analyzer import analyze_telegram_sentiment
from backend.models.sentiment_analysis_params import SentimentAnalysisParams

router = APIRouter()

@router.post("/analyze-sentiment")
async def analyze_sentiment(params: SentimentAnalysisParams):
    try:
        # Ensure we await the analysis results
        analysis_result = await analyze_telegram_sentiment(
            params.telegram_channel,
            params.interval_days,
            params.advanced_analysis
        )
        
        # Convert any coroutines in the result to their values
        if hasattr(analysis_result, '__await__'):
            analysis_result = await analysis_result
            
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze sentiment: {str(e)}"
        ) 