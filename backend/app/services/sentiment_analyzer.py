async def analyze_telegram_sentiment(channel: str, interval_days: int, advanced: bool = False):
    try:
        # Basic metrics
        messages = await fetch_telegram_messages(channel, interval_days)
        basic_metrics = calculate_basic_metrics(messages)
        
        result = {
            "channel_stats": basic_metrics.channel_stats,
            "sentiment_metrics": basic_metrics.sentiment_metrics,
            "topic_analysis": basic_metrics.topic_analysis
        }
        
        # Advanced metrics if requested
        if advanced:
            advanced_metrics = await calculate_advanced_metrics(messages)
            result["advanced_metrics"] = advanced_metrics
            
        return result
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        raise 