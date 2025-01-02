from typing import Dict
from decimal import Decimal
import pandas as pd
from datetime import datetime, timedelta
from .telegram_client import TelegramAnalyzer
import os
from dotenv import load_dotenv

class SentimentAnalyzer:
    def __init__(self):
        load_dotenv()
        self.telegram = TelegramAnalyzer(
            api_id=os.getenv('TELEGRAM_API_ID'),
            api_hash=os.getenv('TELEGRAM_API_HASH')
        )

    async def analyze_channel(self, channel: str, days: int) -> Dict:
        """Analyze sentiment for a Telegram channel"""
        try:
            print(f"[Sentiment] 📊 Analyzing channel {channel} for past {days} days...")
            if not self.telegram.client.is_connected():
                print("[Sentiment] 🔄 Reconnecting Telegram client...")
                await self.telegram.ensure_initialized()
            result = await self.telegram.analyze_channel(channel, days)
            print("[Sentiment] ✅ Analysis complete")
            return result
        except Exception as e:
            print(f"[Sentiment] ❌ Error analyzing channel {channel}: {str(e)}")
            if "403" in str(e):
                print("[Sentiment] ❗ Access forbidden - Please check channel URL and bot permissions")
            return self._get_default_response()

    def _get_default_response(self) -> Dict:
        """Return default response for error cases"""
        return {
            'channel_stats': {
                'total_members': 0,
                'active_members': 0,
                'messages_per_day': 0
            },
            'engagement_metrics': {
                'messages_per_user': 0,
                'avg_message_length': 0,
                'engagement_rate': 0,
                'peak_hours': []
            },
            'sentiment_metrics': {
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0,
                'net_sentiment_score': 0,
                'sentiment_trend': []
            },
            'topic_analysis': {
                'top_topics': [],
                'topic_trends': []
            }
        } 