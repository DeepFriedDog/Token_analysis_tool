from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timedelta
from textblob import TextBlob
import nltk
from collections import Counter, defaultdict
import pytz

class TelegramAnalyzer:
    def __init__(self, api_id: str, api_hash: str):
        load_dotenv()
        session_name = 'sentiment_session'
        
        # Get credentials from env
        self.phone = os.getenv('TELEGRAM_PHONE')
        self.password = os.getenv('TELEGRAM_PASSWORD')
        
        if not self.phone or not self.password:
            raise ValueError("TELEGRAM_PHONE and TELEGRAM_PASSWORD must be set in .env file")
            
        self.client = TelegramClient(
            session_name, 
            api_id, 
            api_hash,
            system_version="4.16.30-vxCUSTOM",
            device_model="Desktop"
        )
        
        # Download required NLTK resources
        try:
            nltk.download('punkt')
            nltk.download('stopwords')
            self.stopwords = set(nltk.corpus.stopwords.words('english'))
        except Exception as e:
            print(f"[Telegram] ⚠️ Error downloading NLTK resources: {str(e)}")
            self.stopwords = set()
            
        self._initialized = False

    async def ensure_initialized(self):
        if not self._initialized:
            try:
                if not self.client.is_connected():
                    await self.client.connect()
                if not await self.client.is_user_authorized():
                    print(f"[Telegram] 🔑 Logging in with phone: {self.phone}")
                    await self.client.start(phone=self.phone, password=self.password)
                self._initialized = True
                print("[Telegram] ✅ Successfully initialized client")
            except Exception as e:
                print(f"[Telegram] ❌ Error during initialization: {str(e)}")
                raise

    async def analyze_channel(self, channel_url: str, days: int = 30) -> dict:
        await self.ensure_initialized()
        
        try:
            channel = channel_url.replace('https://t.me/', '')
            channel = channel.replace('@', '')
            channel = channel.strip('/')
            
            print(f"[Telegram] 🔍 Analyzing channel: {channel}")
            
            async with self.client:
                try:
                    channel_entity = await self.client.get_entity(channel)
                except ValueError as e:
                    print(f"[Telegram] ❌ Could not find channel: {channel}")
                    raise ValueError(f"Channel not found: {channel}") from e
                    
                full_channel = await self.client(GetFullChannelRequest(channel=channel_entity))
                
                end_date = datetime.now(pytz.UTC)
                start_date = end_date - timedelta(days=days)
                
                messages = []
                print(f"[Telegram] 📥 Fetching messages from {start_date.strftime('%Y-%m-%d %H:%M:%S')}")
                
                async for message in self.client.iter_messages(
                    channel_entity,
                    limit=None,
                    offset_date=start_date,
                    wait_time=2
                ):
                    if not message or not message.text:
                        continue
                        
                    if message.date < start_date:
                        continue
                        
                    if message.date > end_date:
                        continue
                    
                    messages.append({
                        'text': message.text,
                        'date': message.date,
                        'views': message.views or 0,
                        'sender_id': message.sender_id,
                        'forwards': message.forwards or 0
                    })
                    
                    if len(messages) % 50 == 0:
                        print(f"[Telegram] 📥 Fetched {len(messages)} messages...")
                
                print(f"[Telegram] ✅ Fetched total {len(messages)} messages")
                
                # Calculate metrics
                total_members = full_channel.full_chat.participants_count
                active_members = len(set(m['sender_id'] for m in messages if m['sender_id'] is not None))
                messages_per_day = len(messages) / days if days > 0 else 0

                return await self._analyze_messages(messages, total_members, active_members, messages_per_day)
            
        except Exception as e:
            print(f"[Telegram] ❌ Error during analysis: {str(e)}")
            raise

    def _calculate_growth_rate(self, participants, days: int) -> float:
        total_members = participants.count
        new_members = sum(1 for p in participants.participants if p.date > datetime.now(pytz.UTC) - timedelta(days=days))
        return (new_members / total_members * 100) if total_members > 0 else 0

    def _calculate_churn_rate(self, participants, days: int) -> float:
        # Estimate churn based on activity patterns
        total_members = participants.count
        inactive_members = sum(1 for p in participants.participants if p.date < datetime.now(pytz.UTC) - timedelta(days=days))
        return (inactive_members / total_members * 100) if total_members > 0 else 0

    async def _analyze_messages(self, messages: list, total_members: int, active_members: int, messages_per_day: float) -> dict:
        sentiment_results = self._analyze_sentiment(messages)
        engagement_results = self._analyze_engagement(messages)
        topic_results = self._analyze_topics(messages)
        peak_hours = self._analyze_peak_hours(messages)
        
        return {
            'channel_stats': {
                'total_members': total_members,
                'active_members': active_members,
                'messages_per_day': messages_per_day
            },
            'engagement_metrics': {
                **engagement_results,
                'peak_hours': peak_hours
            },
            'sentiment_metrics': sentiment_results,
            'topic_analysis': topic_results
        }

    def _analyze_peak_hours(self, messages: list) -> list:
        if not messages:
            return []
            
        # Count messages per hour
        hour_counts = defaultdict(int)
        for msg in messages:
            hour_counts[msg['date'].hour] += 1
            
        total_messages = sum(hour_counts.values())
        
        # Get top 5 peak hours with percentages
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [
            {
                'hour': hour,
                'message_count': count,
                'percentage': (count / total_messages * 100) if total_messages > 0 else 0
            }
            for hour, count in peak_hours
        ]

    def _analyze_topics(self, messages: list) -> dict:
        if not messages:
            return {
                'top_topics': [],
                'topic_trends': []
            }
            
        # Process messages by date for trend analysis
        topics_by_date = defaultdict(Counter)
        words = []
        
        for msg in messages:
            try:
                text = msg['text'].lower()
                # Use simple word splitting instead of nltk tokenization
                msg_words = [
                    word for word in text.split()
                    if word.isalnum() and 
                    word not in self.stopwords and 
                    len(word) > 2  # Filter out very short words
                ]
                words.extend(msg_words)
                
                date_key = msg['date'].date().isoformat()
                topics_by_date[date_key].update(msg_words)
            except Exception as e:
                print(f"[Telegram] ⚠️ Skipping message due to processing error")
                continue
        
        # Get overall top topics with sentiment
        word_freq = Counter(words)
        top_topics = word_freq.most_common(10)
        
        top_topics_with_sentiment = []
        for topic, count in top_topics:
            topic_messages = [
                msg['text'] for msg in messages
                if topic in msg['text'].lower()
            ]
            sentiment_score = sum(TextBlob(msg).sentiment.polarity for msg in topic_messages) / len(topic_messages) if topic_messages else 0
            
            top_topics_with_sentiment.append({
                'topic': topic,
                'frequency': count,
                'sentiment_score': round(sentiment_score, 3)
            })
        
        topic_trends = [
            {
                'date': date,
                'topics': [
                    {'topic': topic, 'count': count}
                    for topic, count in date_counts.most_common(5)
                ]
            }
            for date, date_counts in topics_by_date.items()
        ]
        
        return {
            'top_topics': top_topics_with_sentiment,
            'topic_trends': sorted(topic_trends, key=lambda x: x['date'])
        }

    def _analyze_sentiment(self, messages: list) -> dict:
        if not messages:
            return {
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 0,
                'net_sentiment_score': 0,
                'sentiment_trend': []
            }
            
        # Calculate overall sentiment
        sentiments = [TextBlob(msg['text']).sentiment.polarity for msg in messages]
        positive = sum(1 for s in sentiments if s > 0.1)
        negative = sum(1 for s in sentiments if s < -0.1)
        neutral = sum(1 for s in sentiments if -0.1 <= s <= 0.1)
        total = len(sentiments)
        
        # Calculate sentiment trend by day
        sentiment_by_day = defaultdict(list)
        for msg, sentiment in zip(messages, sentiments):
            date_key = msg['date'].date()
            sentiment_by_day[date_key].append(sentiment)
        
        sentiment_trend = [
            {
                'date': date.isoformat(),
                'score': sum(scores) / len(scores) if scores else 0
            }
            for date, scores in sorted(sentiment_by_day.items())
        ]

        return {
            'positive_percentage': (positive / total) * 100 if total > 0 else 0,
            'negative_percentage': (negative / total) * 100 if total > 0 else 0,
            'neutral_percentage': (neutral / total) * 100 if total > 0 else 0,
            'net_sentiment_score': sum(sentiments) / len(sentiments) if sentiments else 0,
            'sentiment_trend': sentiment_trend
        }

    def _analyze_engagement(self, messages: list) -> dict:
        if not messages:
            return {
                'messages_per_user': 0,
                'avg_message_length': 0,
                'engagement_rate': 0,
                'peak_hours': []
            }
            
        unique_users = len(set(m['sender_id'] for m in messages))
        avg_length = sum(len(m['text']) for m in messages) / len(messages)
        
        hours = [m['date'].hour for m in messages]
        hour_counts = Counter(hours)
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'messages_per_user': len(messages) / unique_users if unique_users > 0 else 0,
            'avg_message_length': avg_length,
            'engagement_rate': sum(m['views'] or 0 for m in messages) / len(messages),
            'peak_hours': [hour for hour, _ in peak_hours]
        } 