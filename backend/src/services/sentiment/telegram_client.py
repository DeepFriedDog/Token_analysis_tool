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
import hashlib
import statistics

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
                
                active_members = len(set(m['sender_id'] for m in messages if m['sender_id'] is not None))
                messages_per_day = len(messages) / days if days > 0 else 0
                messages_per_day_per_user = messages_per_day / active_members if active_members > 0 else 0
                
                # Basic analysis
                result = {
                    'channel_stats': {
                        'total_members': total_members,
                        'active_members': active_members,
                        'messages_per_day': messages_per_day_per_user
                    },
                    'engagement_metrics': self._analyze_engagement(messages),
                    'sentiment_metrics': self._analyze_sentiment(messages),
                    'topic_analysis': self._analyze_topics(messages)
                }
                
                # Add advanced metrics if requested
                if advanced_mode:
                    print("[Telegram] 📊 Calculating advanced metrics...")
                    result['advanced_metrics'] = await self._analyze_advanced_metrics(messages)
                    print("[Telegram] ✅ Advanced metrics complete")
                    print(f"[Telegram] Advanced metrics data: {result['advanced_metrics']}")  # Debug log
                
                return result
                
        except Exception as e:
            print(f"[Telegram] ❌ Error during analysis: {str(e)}")
            raise

    async def _analyze_advanced_metrics(self, messages: list) -> dict:
        """Analyze advanced metrics including discussion quality and manipulation indicators"""
        try:
            # Initialize counters
            technical_terms = defaultdict(int)
            detailed_messages = 0
            reference_links = 0
            total_words = 0
            duplicate_messages = defaultdict(int)
            user_message_counts = defaultdict(int)
            
            # Technical terms to track
            tech_categories = {
                'defi': ['liquidity', 'yield', 'stake', 'farm', 'pool', 'swap'],
                'security': ['audit', 'multisig', 'timelock', 'vulnerability', 'exploit'],
                'development': ['github', 'code', 'smart contract', 'implementation', 'deploy'],
                'governance': ['proposal', 'vote', 'dao', 'governance', 'quorum']
            }
            
            # Analyze each message
            for msg in messages:
                text = msg['text'].lower()
                words = text.split()
                total_words += len(words)
                
                # Track technical terms
                for category, terms in tech_categories.items():
                    if any(term in text for term in terms):
                        technical_terms[category] += 1
                
                # Track detailed messages
                if len(words) > 50:
                    detailed_messages += 1
                
                # Track reference links
                if any(domain in text for domain in ['github.com', 'docs.', 'gitbook.']):
                    reference_links += 1
                
                # Track duplicate messages for spam detection
                msg_hash = hashlib.md5(text.encode()).hexdigest()
                duplicate_messages[msg_hash] += 1
                
                # Track user message frequency
                user_message_counts[msg['sender_id']] += 1
            
            # Calculate metrics
            total_messages = len(messages)
            unique_users = len(user_message_counts)
            
            # Discussion depth metrics
            discussion_depth = {
                'technical_term_frequency': dict(technical_terms),
                'detailed_messages_count': detailed_messages,
                'reference_links_count': reference_links,
                'avg_message_complexity': total_words / total_messages if total_messages > 0 else 0
            }
            
            # Calculate pump indicators
            duplicate_ratio = sum(1 for count in duplicate_messages.values() if count > 1) / total_messages if total_messages > 0 else 0
            suspicious_users = sum(1 for count in user_message_counts.values() if count > 50) / unique_users if unique_users > 0 else 0
            
            pump_indicators = {
                'hype_level': self._calculate_hype_level(messages),
                'duplicate_message_ratio': duplicate_ratio,
                'suspicious_user_ratio': suspicious_users,
                'coordinated_spikes': self._detect_activity_spikes(messages)
            }
            
            # Calculate quality indicators
            quality_indicators = {
                'technical_discussion_ratio': sum(technical_terms.values()) / total_messages if total_messages > 0 else 0,
                'quality_contributor_ratio': sum(1 for count in user_message_counts.values() if count > 5) / unique_users if unique_users > 0 else 0,
                'avg_message_quality': (detailed_messages + reference_links) / total_messages if total_messages > 0 else 0
            }
            
            return {
                'discussion_depth': discussion_depth,
                'pump_indicators': pump_indicators,
                'quality_indicators': quality_indicators
            }
            
        except Exception as e:
            print(f"[Telegram] ❌ Error analyzing advanced metrics: {str(e)}")
            raise

    def _calculate_hype_level(self, messages: list) -> float:
        """Calculate hype level based on message patterns"""
        hype_words = ['moon', 'pump', 'buy', 'fomo', 'rocket', '🚀', '🌙', '💎']
        hype_count = sum(1 for msg in messages if any(word in msg['text'].lower() for word in hype_words))
        return hype_count / len(messages) if messages else 0

    def _detect_activity_spikes(self, messages: list) -> int:
        """Detect unusual spikes in message activity"""
        if not messages:
            return 0
            
        # Group messages by hour
        hour_counts = defaultdict(int)
        for msg in messages:
            hour_key = msg['date'].replace(minute=0, second=0, microsecond=0)
            hour_counts[hour_key] += 1
            
        # Calculate mean and standard deviation
        counts = list(hour_counts.values())
        mean = statistics.mean(counts)
        stdev = statistics.stdev(counts) if len(counts) > 1 else 0
        
        # Count hours with activity > 2 standard deviations above mean
        return sum(1 for count in counts if count > mean + (2 * stdev))

    def _get_peak_activity_days(self, messages: list) -> list:
        day_counts = defaultdict(int)
        for msg in messages:
            day_counts[msg['date'].strftime('%A')] += 1
        
        return [
            {'day': day, 'message_count': count}
            for day, count in sorted(
                day_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
        ]

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
        # Get sentiment metrics
        sentiment_results = self._analyze_sentiment(messages)
        
        # Get engagement metrics with peak hours
        engagement_results = self._analyze_engagement(messages)
        
        # Get topic analysis with frequency and trends
        topic_results = self._analyze_topics(messages)
        
        # Calculate peak activity patterns
        peak_hours = self._analyze_peak_hours(messages)
        
        # Calculate hourly and daily activity patterns
        activity_patterns = self._analyze_activity_patterns(messages)
        
        return {
            'channel_stats': {
                'total_members': total_members,
                'active_members': active_members,
                'messages_per_day': messages_per_day
            },
            'engagement_metrics': {
                **engagement_results,
                'peak_hours': peak_hours,
                'activity_patterns': activity_patterns
            },
            'sentiment_metrics': sentiment_results,
            'topic_analysis': topic_results
        }

    def _analyze_activity_patterns(self, messages: list) -> dict:
        if not messages:
            return {
                'hourly_distribution': [],
                'daily_distribution': [],
                'peak_periods': {
                    'hours': [],
                    'days': []
                }
            }
        
        # Analyze hourly patterns
        hour_counts = defaultdict(int)
        day_counts = defaultdict(int)
        
        for msg in messages:
            hour_counts[msg['date'].hour] += 1
            day_counts[msg['date'].strftime('%A')] += 1  # Get day name
        
        total_messages = len(messages)
        
        # Get hourly distribution
        hourly_distribution = [
            {
                'hour': hour,
                'message_count': count,
                'percentage': (count / total_messages * 100) if total_messages > 0 else 0
            }
            for hour, count in sorted(hour_counts.items())
        ]
        
        # Get daily distribution
        daily_distribution = [
            {
                'day': day,
                'message_count': count,
                'percentage': (count / total_messages * 100) if total_messages > 0 else 0
            }
            for day, count in sorted(day_counts.items())
        ]
        
        # Identify peak periods
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        peak_days = sorted(day_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'hourly_distribution': hourly_distribution,
            'daily_distribution': daily_distribution,
            'peak_periods': {
                'hours': [{'hour': h, 'count': c} for h, c in peak_hours],
                'days': [{'day': d, 'count': c} for d, c in peak_days]
            }
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
            
        # Calculate overall sentiment using TextBlob
        sentiments = []
        for msg in messages:
            try:
                blob = TextBlob(msg['text'])
                sentiments.append(blob.sentiment.polarity)
            except Exception as e:
                print(f"[Telegram] ⚠️ Error analyzing sentiment: {str(e)}")
                continue
        
        # Classify messages
        positive = sum(1 for s in sentiments if s > 0.1)
        negative = sum(1 for s in sentiments if s < -0.1)
        neutral = sum(1 for s in sentiments if -0.1 <= s <= 0.1)
        total = len(sentiments)
        
        # Calculate daily sentiment trend
        sentiment_by_day = defaultdict(list)
        for msg, sentiment in zip(messages, sentiments):
            date_key = msg['date'].date()
            sentiment_by_day[date_key].append(sentiment)
        
        sentiment_trend = [
            {
                'date': date.isoformat(),
                'net_score': sum(scores) / len(scores) if scores else 0
            }
            for date, scores in sorted(sentiment_by_day.items())
        ]
        
        return {
            'positive_percentage': (positive / total * 100) if total > 0 else 0,
            'negative_percentage': (negative / total * 100) if total > 0 else 0,
            'neutral_percentage': (neutral / total * 100) if total > 0 else 0,
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
            
        # Count messages per unique user
        user_message_counts = defaultdict(int)
        for msg in messages:
            if msg['sender_id'] is not None:
                user_message_counts[msg['sender_id']] += 1
        
        active_users = len(user_message_counts)
        total_messages = len(messages)
        
        # Average messages per active user
        messages_per_user = total_messages / active_users if active_users > 0 else 0
        avg_length = sum(len(m['text']) for m in messages) / total_messages if total_messages > 0 else 0
        
        return {
            'messages_per_user': messages_per_user,
            'avg_message_length': avg_length,
            'engagement_rate': sum(m['views'] or 0 for m in messages) / total_messages if total_messages > 0 else 0,
            'peak_hours': self._analyze_peak_hours(messages)
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