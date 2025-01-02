import React from 'react';
import { StatCard } from './StatCard';
import { SentimentAnalysis } from '../types/sentiment';

interface Props {
  advancedMetrics: NonNullable<SentimentAnalysis['advanced_metrics']>;
}

export const AdvancedMetrics: React.FC<Props> = ({ advancedMetrics }) => {
  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg p-4 shadow">
        <h3 className="text-xl font-semibold mb-4">Top Community Members</h3>
        <div className="space-y-2">
          {advancedMetrics?.top_users?.slice(0, 5).map((user, index) => (
            <div key={user.user_id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
              <span className="font-medium">#{index + 1}</span>
              <span>Messages: {user.message_count}</span>
              <span>Reactions: {user.reaction_count}</span>
              <span>Score: {user.engagement_score.toFixed(1)}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg p-4 shadow">
        <h3 className="text-xl font-semibold mb-4">Popular Reactions</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {advancedMetrics?.reaction_stats?.slice(0, 5).map((reaction) => (
            <div key={reaction.reaction} className="text-center p-2 bg-gray-50 rounded">
              <div className="text-xl mb-1">{reaction.reaction}</div>
              <div className="text-sm text-gray-600">{reaction.count} ({reaction.percentage.toFixed(1)}%)</div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg p-4 shadow">
        <h3 className="text-xl font-semibold mb-4">Activity Patterns</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <StatCard
            title="Daily Active Users"
            value={advancedMetrics.activity_patterns.daily_active_users}
            type="number"
          />
          <StatCard
            title="Weekly Active Users"
            value={advancedMetrics.activity_patterns.weekly_active_users}
            type="number"
          />
          <StatCard
            title="Monthly Active Users"
            value={advancedMetrics.activity_patterns.monthly_active_users}
            type="number"
          />
        </div>
      </div>
    </div>
  );
}; 