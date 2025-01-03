interface SentimentMetrics {
  positive_percentage: number;
  neutral_percentage: number;
  negative_percentage: number;
  net_sentiment_score: number;
  sentiment_trend: Array<{
    date: string;
    net_score: number;
  }>;
}

export interface SentimentAnalysis {
  channel_stats: {
    total_members: number;
    active_members: number;
    messages_per_day: number;
  };
  sentiment_metrics: SentimentMetrics;
  topic_analysis: {
    top_topics: Array<{
      topic: string;
      frequency: number;
    }>;
  };
  activity_patterns: {
    daily_metrics: Array<{
      date: string;
      active_users: number;
      message_count: number;
    }>;
    retention: {
      consistent_users: number;
      occasional_users: number;
      one_time_users: number;
    };
    activity_consistency: {
      average_gap_hours: number;
      max_gap_hours: number;
      activity_score: number;
    };
  };
  advanced_metrics: {
    discussion_depth: {
      technical_term_frequency: Record<string, number>;
      detailed_messages_count: number;
      reference_links_count: number;
      avg_message_complexity: number;
    };
    pump_indicators: {
      hype_level: number;
      duplicate_message_ratio: number;
      suspicious_user_ratio: number;
      coordinated_spikes: number;
    };
    quality_indicators: {
      technical_discussion_ratio: number;
      quality_contributor_ratio: number;
      avg_message_quality: number;
    };
  };
}

export interface SentimentAnalysisParams {
  telegram_channel: string;
  interval_days: number;
  advanced_analysis: boolean;
}