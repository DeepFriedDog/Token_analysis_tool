import React from 'react';
import { formatPrice, formatPercentage } from '../utils/format';

interface ExitSignalsProps {
  signals: Array<{
    price: number;
    type: 'stop_loss' | 'take_profit';
    confidence: number;
    reasoning?: string[];
  }>;
  currentPrice: number;
  technicalSignals: {
    macd: string;
    bb: string;
  };
}

export const ExitSignals: React.FC<ExitSignalsProps> = ({ 
  signals, 
  currentPrice, 
  technicalSignals 
}) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow mb-8">
      <h2 className="text-xl font-semibold mb-4">Exit Strategy</h2>
      
      {/* Technical Signals */}
      <div className="mb-6">
        <h3 className="font-medium mb-3">Technical Signals</h3>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">MACD Signal: {technicalSignals.macd}</span>
            <span className="text-gray-600">NEUTRAL</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">BB Signal: {technicalSignals.bb}</span>
            <span className="text-red-600">UPPER BREAK</span>
          </div>
        </div>
      </div>

      {/* Exit Points */}
      <div>
        <h3 className="font-medium mb-3">Exit Points</h3>
        <div className="space-y-2">
          {signals.map((signal, index) => (
            <div key={index} className="flex justify-between items-center py-1">
              <div className="flex items-center gap-3">
                <span>${formatPrice(signal.price)}</span>
                <span className="text-sm text-gray-500">
                  Position Size: ${formatPrice(signal.confidence * 100)}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className={signal.type === 'take_profit' ? 'text-green-600' : 'text-red-600'}>
                  {signal.type === 'take_profit' ? '+' : '-'}
                  {formatPercentage(Math.abs((signal.price - currentPrice) / currentPrice * 100))}
                </span>
                <span className="text-gray-400">→</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Trading Stop Loss */}
      <div className="mt-6 pt-4 border-t">
        <h3 className="font-medium mb-2">Trading Stop Loss</h3>
        <p className="text-sm text-gray-500 italic">
          Set a dynamic stop loss automatically with price movement!
        </p>
      </div>
    </div>
  );
}; 