export interface SentimentAnalysis {
  channel_stats: {
    total_members: number;
    active_members: number;
    messages_per_day: number;
  };
  engagement_metrics: {
    messages_per_user: number;
    avg_message_length: number;
    engagement_rate: number;
    peak_hours: Array<{
      hour: number;
      message_count: number;
      percentage: number;
    }>;
  };
  sentiment_metrics: {
    positive_percentage: number;
    negative_percentage: number;
    neutral_percentage: number;
    net_sentiment_score: number;
    sentiment_trend: Array<{
      date: string;
      score: number;
    }>;
  };
  topic_analysis: {
    top_topics: Array<{
      topic: string;
      frequency: number;
      sentiment_score: number;
    }>;
    topic_trends: Array<{
      date: string;
      topics: Array<{
        topic: string;
        count: number;
      }>;
    }>;
  };
}

export interface SentimentAnalysisParams {
  telegram_channel: string;
  interval_days: number;
} 