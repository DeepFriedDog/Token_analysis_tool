import React from 'react';
import { StatCard } from './StatCard';
import { SentimentAnalysis as SentimentData } from '../types/sentiment';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, 
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

interface Props {
  data: SentimentData;
  loading: boolean;
}

export const SentimentAnalysis: React.FC<Props> = ({ data, loading }) => {
  if (loading) {
    return <div className="animate-pulse">Loading sentiment analysis...</div>;
  }

  return (
    <div className="space-y-6 p-4">
      <h2 className="text-2xl font-bold">Community Sentiment Analysis</h2>
      
      {/* Channel Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
          title="Messages/Day"
          value={data.channel_stats.messages_per_day}
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
                value: data.sentiment_metrics.positive_percentage
              },
              {
                name: 'Neutral',
                value: data.sentiment_metrics.neutral_percentage
              },
              {
                name: 'Negative',
                value: data.sentiment_metrics.negative_percentage
              }
            ]}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#4F46E5" />
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
    </div>
  );
}; 