import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

interface SentimentMetricsProps {
  discussionDepth: {
    technical_term_frequency: Record<string, number>;
    detailed_messages_count: number;
    reference_links_count: number;
    avg_message_complexity: number;
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
  activityPatterns: {
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
  sentimentTrends: {
    sentiment_trend: Array<{
      date: string;
      net_score: number;
    }>;
    overall_sentiment: number;
  };
}

export const SentimentMetrics: React.FC<SentimentMetricsProps> = ({ 
  discussionDepth, 
  activityPatterns,
  sentimentTrends 
}) => {
  return (
    <div className="space-y-6">
      {/* Discussion Depth Section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Discussion Quality Analysis</h2>
        
        <div className="grid grid-cols-2 gap-6">
          {/* Technical Terms */}
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="font-medium mb-3">Technical Discussion</h3>
            <div className="space-y-2">
              {Object.entries(discussionDepth.technical_term_frequency).map(([category, count]) => (
                <div key={category} className="flex justify-between items-center">
                  <span className="text-gray-600 capitalize">{category.replace('_', ' ')}:</span>
                  <span>{count} mentions</span>
                </div>
              ))}
            </div>
          </div>

          {/* Message Complexity */}
          <div className="bg-gray-50 p-4 rounded">
            <h3 className="font-medium mb-3">Discussion Depth</h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Detailed Messages:</span>
                <span>{discussionDepth.detailed_messages_count}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Reference Links:</span>
                <span>{discussionDepth.reference_links_count}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Avg Message Length:</span>
                <span>{Math.round(discussionDepth.avg_message_complexity)} words</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* New Pump Detection Section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Market Manipulation Indicators</h2>
        <div className="grid grid-cols-2 gap-6">
          {/* Pump Indicators */}
          <div className="bg-red-50 p-4 rounded">
            <h3 className="font-medium mb-3">Risk Indicators</h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Hype Level:</span>
                <span className={`${discussionDepth.pump_indicators.hype_level > 0.5 ? 'text-red-600' : 'text-gray-600'}`}>
                  {(discussionDepth.pump_indicators.hype_level * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Duplicate Messages:</span>
                <span className={`${discussionDepth.pump_indicators.duplicate_message_ratio > 0.3 ? 'text-red-600' : 'text-gray-600'}`}>
                  {(discussionDepth.pump_indicators.duplicate_message_ratio * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Suspicious Users:</span>
                <span className={`${discussionDepth.pump_indicators.suspicious_user_ratio > 0.2 ? 'text-red-600' : 'text-gray-600'}`}>
                  {(discussionDepth.pump_indicators.suspicious_user_ratio * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Activity Spikes:</span>
                <span className={`${discussionDepth.pump_indicators.coordinated_spikes > 3 ? 'text-red-600' : 'text-gray-600'}`}>
                  {discussionDepth.pump_indicators.coordinated_spikes}
                </span>
              </div>
            </div>
          </div>

          {/* Quality Indicators */}
          <div className="bg-green-50 p-4 rounded">
            <h3 className="font-medium mb-3">Quality Indicators</h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Technical Discussion:</span>
                <span className={`${discussionDepth.quality_indicators.technical_discussion_ratio > 0.3 ? 'text-green-600' : 'text-gray-600'}`}>
                  {(discussionDepth.quality_indicators.technical_discussion_ratio * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Quality Contributors:</span>
                <span className={`${discussionDepth.quality_indicators.quality_contributor_ratio > 0.2 ? 'text-green-600' : 'text-gray-600'}`}>
                  {(discussionDepth.quality_indicators.quality_contributor_ratio * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Message Quality Score:</span>
                <span className={`${discussionDepth.quality_indicators.avg_message_quality > 0.5 ? 'text-green-600' : 'text-gray-600'}`}>
                  {(discussionDepth.quality_indicators.avg_message_quality * 100).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sentiment Trend Chart */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Sentiment Trend Over Time</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={sentimentTrends.sentiment_trend}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(date) => {
                  const d = new Date(date);
                  return `${d.getMonth() + 1}/${d.getDate()}`;
                }}
              />
              <YAxis 
                domain={[-1, 1]}
                ticks={[-1, -0.5, 0, 0.5, 1]}
                tickFormatter={(value) => value.toFixed(2)}
              />
              <Tooltip 
                formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, "Sentiment"]}
                labelFormatter={(date) => new Date(date).toLocaleDateString()}
              />
              <Line
                type="monotone"
                dataKey="net_score"
                stroke="#8884d8"
                strokeWidth={2}
                dot={false}
                name="Net Sentiment"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Activity Patterns Section */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Community Engagement</h2>
        
        {/* User Retention */}
        <div className="mb-6">
          <h3 className="font-medium mb-3">User Retention</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-green-50 p-4 rounded text-center">
              <div className="text-2xl font-bold text-green-600">
                {activityPatterns.retention.consistent_users}
              </div>
              <div className="text-sm text-gray-600">Consistent Users</div>
            </div>
            <div className="bg-yellow-50 p-4 rounded text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {activityPatterns.retention.occasional_users}
              </div>
              <div className="text-sm text-gray-600">Occasional Users</div>
            </div>
            <div className="bg-red-50 p-4 rounded text-center">
              <div className="text-2xl font-bold text-red-600">
                {activityPatterns.retention.one_time_users}
              </div>
              <div className="text-sm text-gray-600">One-time Users</div>
            </div>
          </div>
        </div>

        {/* Activity Consistency */}
        <div>
          <h3 className="font-medium mb-3">Activity Metrics</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded text-center">
              <div className="text-xl font-semibold">
                {activityPatterns.activity_consistency.average_gap_hours.toFixed(1)}h
              </div>
              <div className="text-sm text-gray-600">Average Gap</div>
            </div>
            <div className="bg-blue-50 p-4 rounded text-center">
              <div className="text-xl font-semibold">
                {activityPatterns.activity_consistency.max_gap_hours.toFixed(1)}h
              </div>
              <div className="text-sm text-gray-600">Max Gap</div>
            </div>
            <div className="bg-blue-50 p-4 rounded text-center">
              <div className="text-xl font-semibold">
                {(activityPatterns.activity_consistency.activity_score * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Activity Score</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 