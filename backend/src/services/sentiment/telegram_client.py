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

    async def analyze_channel(self, channel_url: str, days: int = 30, advanced_mode: bool = False) -> dict:
        await self.ensure_initialized()
        
        try:
            channel = channel_url.replace('https://t.me/', '').replace('@', '').replace('t.me/', '').strip('/')
            print(f"[Telegram] 🔍 Analyzing channel: {channel} for the past {days} days")
            print(f"[Telegram] 📊 Mode: {'Advanced' if advanced_mode else 'Basic'}")
            
            async with self.client:
                channel_entity = await self._get_channel_entity(channel)
                full_channel = await self.client(GetFullChannelRequest(channel=channel_entity))
                
                end_date = datetime.now(pytz.UTC)
                start_date = end_date - timedelta(days=days)
                
                messages = await self._fetch_messages(channel_entity, start_date, end_date)
                
                total_members = full_channel.full_chat.participants_count
                
                # Basic mode just counts unique senders
                if not advanced_mode:
                    active_members = len(set(m['sender_id'] for m in messages if m['sender_id'] is not None))
                    messages_per_day = len(messages) / days if days > 0 else 0
                else:
                    # Advanced mode includes full participant analysis
                    active_members = await self._get_active_members(channel_entity, start_date)
                    messages_per_day = (len(messages) / days / active_members) if days > 0 and active_members > 0 else 0
                
                result = await self._analyze_messages(messages, total_members, active_members, messages_per_day)
                
                if advanced_mode:
                    advanced_metrics = await self._analyze_advanced_metrics(channel_entity, messages, start_date)
                    result['advanced_metrics'] = advanced_metrics
                
                return result
                
        except Exception as e:
            print(f"[Telegram] ❌ Error during analysis: {str(e)}")
            raise

    async def _analyze_advanced_metrics(self, channel_entity, messages: list, start_date: datetime) -> dict:
        print("[Telegram] 📊 Calculating advanced metrics...")
        
        # Analyze user activity
        user_stats = defaultdict(lambda: {'message_count': 0, 'reaction_count': 0})
        for msg in messages:
            if msg['sender_id']:
                user_stats[msg['sender_id']]['message_count'] += 1
                # Count reactions if available
                if hasattr(msg, 'reactions') and msg['reactions']:
                    user_stats[msg['sender_id']]['reaction_count'] += len(msg['reactions'])
        
        # Calculate engagement scores and sort users
        top_users = []
        for user_id, stats in user_stats.items():
            engagement_score = stats['message_count'] + (stats['reaction_count'] * 0.5)
            top_users.append({
                'user_id': str(user_id),
                'message_count': stats['message_count'],
                'reaction_count': stats['reaction_count'],
                'engagement_score': engagement_score
            })
        
        top_users.sort(key=lambda x: x['engagement_score'], reverse=True)
        
        # Get reaction statistics
        reaction_counter = Counter()
        total_reactions = 0
        for msg in messages:
            if hasattr(msg, 'reactions') and msg['reactions']:
                for reaction in msg['reactions']:
                    reaction_counter[reaction] += 1
                    total_reactions += 1
        
        reaction_stats = [
            {
                'reaction': reaction,
                'count': count,
                'percentage': (count / total_reactions * 100) if total_reactions > 0 else 0
            }
            for reaction, count in reaction_counter.most_common(10)
        ]
        
        print("[Telegram] ✅ Advanced metrics calculation complete")
        
        return {
            'top_users': top_users[:10],  # Limit to top 10 users
            'reaction_stats': reaction_stats,
            'activity_patterns': {
                'daily_active_users': len(set(m['sender_id'] for m in messages if m['date'] > datetime.now(pytz.UTC) - timedelta(days=1))),
                'weekly_active_users': len(set(m['sender_id'] for m in messages if m['date'] > datetime.now(pytz.UTC) - timedelta(days=7))),
                'monthly_active_users': len(set(m['sender_id'] for m in messages if m['date'] > datetime.now(pytz.UTC) - timedelta(days=30)))
            }
        }

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
                print(f"[Telegram] ⚠️ Skipping message due to processing error: {str(e)}")
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

    async def _get_active_members(self, channel_entity, start_date: datetime) -> int:
        try:
            print("[Telegram] 📊 Calculating active members...")
            participants = await self.client.get_participants(channel_entity, limit=None)
            total_participants = len(participants)
            active_count = 0
            processed = 0
            
            for participant in participants:
                try:
                    messages = await self.client.get_messages(
                        channel_entity,
                        from_user=participant,
                        offset_date=start_date,
                        limit=1
                    )
                    if messages and len(messages) > 0:
                        active_count += 1
                    
                    processed += 1
                    if processed % 50 == 0:
                        print(f"[Telegram] 👥 Processed {processed}/{total_participants} participants...")
                        
                except Exception as e:
                    print(f"[Telegram] ⚠️ Error checking participant activity: {str(e)}")
                    continue
                
            print(f"[Telegram] ✅ Found {active_count} active members out of {total_participants}")
            return active_count
        except Exception as e:
            print(f"[Telegram] ❌ Error calculating active members: {str(e)}")
            return 0 

    async def _get_channel_entity(self, channel: str):
        try:
            print(f"[Telegram] 🔍 Getting channel entity for: {channel}")
            try:
                channel_entity = await self.client.get_entity(channel)
            except ValueError as e:
                print(f"[Telegram] ❌ Could not find channel: {channel}")
                raise ValueError(f"Channel not found: {channel}") from e
            
            return channel_entity
        except Exception as e:
            print(f"[Telegram] ❌ Error getting channel entity: {str(e)}")
            raise 

    async def _fetch_messages(self, channel_entity, start_date: datetime, end_date: datetime) -> list:
        try:
            print(f"[Telegram] 📥 Fetching messages from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
            messages = []
            
            async for message in self.client.iter_messages(
                channel_entity,
                offset_date=end_date,
                limit=None
            ):
                if message.date < start_date:
                    break
                    
                if not message.text:
                    continue
                    
                messages.append({
                    'text': message.text,
                    'date': message.date,
                    'views': getattr(message, 'views', 0),
                    'sender_id': message.sender_id,
                    'reactions': getattr(message, 'reactions', [])
                })
                
                if len(messages) % 100 == 0:
                    print(f"[Telegram] 📝 Fetched {len(messages)} messages...")
                    
            print(f"[Telegram] ✅ Successfully fetched {len(messages)} messages")
            return messages
            
        except Exception as e:
            print(f"[Telegram] ❌ Error fetching messages: {str(e)}")
            raise 