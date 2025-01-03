import React from 'react';
import { StatCard } from './StatCard';
import { SentimentAnalysis as SentimentData } from '../types/sentiment';
import { AdvancedMetrics } from './AdvancedMetrics';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, 
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { SentimentMetrics } from './SentimentMetrics';

interface Props {
  data: SentimentData;
  loading: boolean;
}

export const SentimentAnalysis: React.FC<Props> = ({ data, loading }) => {
  if (loading) {
    return <div className="animate-pulse">Loading sentiment analysis...</div>;
  }

  const activeUsersPercentage = data.channel_stats.total_members > 0
    ? Number(((data.channel_stats.active_members / data.channel_stats.total_members) * 100).toFixed(1))
    : 0;

  return (
    <div className="space-y-6 p-4">
      <h2 className="text-2xl font-bold">Community Sentiment Analysis</h2>
      
      {/* Channel Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Members"
          value={data.channel_stats.total_members}
          type="number"
        />
        <StatCard
          title="Active Members"
          value={data.channel_stats.active_members}
          type="number"
        />
        <StatCard
          title="Active Members %"
          value={activeUsersPercentage}
          type="number"
        />
        <StatCard
          title="Avg Messages/Day/User"
          value={Number(data.channel_stats.messages_per_day.toFixed(1))}
          type="number"
        />
      </div>

      {/* Sentiment Distribution */}
      <div className="bg-white rounded-lg p-4 shadow">
        <h3 className="text-xl font-semibold mb-4">Sentiment Distribution</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={[
              {
                name: 'Positive',
                value: data.sentiment_metrics.positive_percentage,
                fill: '#22c55e'  // Green
              },
              {
                name: 'Neutral',
                value: data.sentiment_metrics.neutral_percentage,
                fill: '#3b82f6'  // Blue
              },
              {
                name: 'Negative',
                value: data.sentiment_metrics.negative_percentage,
                fill: '#ef4444'  // Red
              }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top Topics */}
      <div className="bg-white rounded-lg p-4 shadow">
        <h3 className="text-xl font-semibold mb-4">Top Discussion Topics</h3>
        <div className="space-y-2">
          {data.topic_analysis.top_topics.map((topic, index) => (
            <div key={index} className="flex items-center justify-between">
              <span>{topic.topic}</span>
              <span className="text-gray-600">{topic.frequency} mentions</span>
            </div>
          ))}
        </div>
      </div>

      {/* Advanced Metrics Section */}
      {data.advanced_metrics && (
        <div>
          <h2 className="text-2xl font-bold mb-4">Advanced Community Insights</h2>
          <div style={{ display: 'none' }}>
            {JSON.stringify(data.sentiment_metrics, null, 2)}
          </div>
          <SentimentMetrics 
            discussionDepth={{
              technical_term_frequency: data.advanced_metrics.discussion_depth.technical_term_frequency,
              detailed_messages_count: data.advanced_metrics.discussion_depth.detailed_messages_count,
              reference_links_count: data.advanced_metrics.discussion_depth.reference_links_count,
              avg_message_complexity: data.advanced_metrics.discussion_depth.avg_message_complexity,
              pump_indicators: data.advanced_metrics.pump_indicators,
              quality_indicators: data.advanced_metrics.quality_indicators
            }}
            activityPatterns={{
              daily_metrics: data.activity_patterns?.daily_metrics || [],
              retention: data.activity_patterns?.retention || {
                consistent_users: 0,
                occasional_users: 0,
                one_time_users: 0
              },
              activity_consistency: data.activity_patterns?.activity_consistency || {
                average_gap_hours: 0,
                max_gap_hours: 0,
                activity_score: 0
              }
            }}
            sentimentTrends={{
              sentiment_trend: data.sentiment_metrics?.sentiment_trend || [],
              overall_sentiment: data.sentiment_metrics?.net_sentiment_score || 0
            }}
          />
        </div>
      )}
    </div>
  );
}; 