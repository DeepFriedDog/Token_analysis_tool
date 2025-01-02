import React from 'react';
import { formatPrice, formatPercentage } from '../utils/format';

interface ExitStrategyProps {
  strategy: {
    exit_points: Array<{
      price: number;
      percentage: number;
      type?: string;
      allocation_to_exit?: number;
      confidence?: number;
    }>;
    trailing_stop_percent?: number;
    technical_signals: {
      macd_signal?: 'buy' | 'sell' | 'neutral';
      rsi_signal?: 'overbought' | 'oversold' | 'neutral';
      bb_signal?: 'upper_break' | 'lower_break' | 'neutral';
    };
  };
}

export const ExitStrategy: React.FC<ExitStrategyProps> = ({ strategy }) => {
  const { exit_points, trailing_stop_percent = 10, technical_signals } = strategy;

  return (
    <div className="mt-8 bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-4">Exit Strategy</h2>
      
      {/* Technical Signals */}
      <div className="mb-6">
        <h3 className="font-medium mb-2">Technical Signals</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-3 bg-gray-50 rounded">
            <span className="text-gray-600">MACD Signal:</span>
            <span className={`ml-2 font-medium ${
              technical_signals.macd_signal === 'sell' ? 'text-red-600' :
              technical_signals.macd_signal === 'buy' ? 'text-green-600' :
              'text-gray-600'
            }`}>
              {technical_signals.macd_signal?.toUpperCase() || 'NEUTRAL'}
            </span>
          </div>
          <div className="p-3 bg-gray-50 rounded">
            <span className="text-gray-600">RSI Signal:</span>
            <span className={`ml-2 font-medium ${
              technical_signals.rsi_signal === 'overbought' ? 'text-red-600' :
              technical_signals.rsi_signal === 'oversold' ? 'text-green-600' :
              'text-gray-600'
            }`}>
              {technical_signals.rsi_signal?.toUpperCase() || 'NEUTRAL'}
            </span>
          </div>
          <div className="p-3 bg-gray-50 rounded">
            <span className="text-gray-600">BB Signal:</span>
            <span className={`ml-2 font-medium ${
              technical_signals.bb_signal === 'upper_break' ? 'text-red-600' :
              technical_signals.bb_signal === 'lower_break' ? 'text-green-600' :
              'text-gray-600'
            }`}>
              {technical_signals.bb_signal?.replace('_', ' ').toUpperCase() || 'NEUTRAL'}
            </span>
          </div>
        </div>
      </div>

      {/* Exit Points */}
      <div className="mb-6">
        <h3 className="font-medium mb-2">Exit Points</h3>
        {exit_points && exit_points.length > 0 ? (
          <div className="space-y-3">
            {exit_points.map((exit, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                  <span className="text-gray-800 font-semibold">
                    ${formatPrice(exit.price)}
                  </span>
                  <span className="ml-2 text-red-600">
                    (+{formatPercentage(exit.percentage)}%)
                  </span>
                  {exit.allocation_to_exit && (
                    <span className="ml-2 text-blue-600">
                      Exit: {formatPercentage(exit.allocation_to_exit * 100)}%
                    </span>
                  )}
                </div>
                <div className="flex items-center">
                  {exit.type && (
                    <span className="text-gray-500 italic mr-3">[{exit.type}]</span>
                  )}
                  {exit.confidence && (
                    <div className="bg-gray-200 rounded-full h-2 w-20">
                      <div 
                        className="bg-blue-600 rounded-full h-2"
                        style={{ width: `${exit.confidence}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No exit points available</p>
        )}
      </div>

      {/* Trailing Stop */}
      <div className="p-4 bg-gray-50 rounded">
        <h3 className="font-medium mb-2">Trailing Stop Loss</h3>
        <div className="flex items-center justify-between">
          <span className="text-gray-600">Current Stop:</span>
          <span className="text-purple-600 font-medium">
            {trailing_stop_percent}% (Adjusts automatically with price movement)
          </span>
        </div>
      </div>
    </div>
  );
}; 