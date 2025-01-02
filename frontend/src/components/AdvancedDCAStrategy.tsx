import React from 'react';
import { formatPrice, formatPercentage } from '../utils/format';

interface Props {
  strategy: {
    signals: Array<{
      price: number;
      signal_strength: number;
      position_size: number;
    }>;
  };
  investmentAmount: number;
}

export const AdvancedDCAStrategy: React.FC<Props> = ({ strategy, investmentAmount }) => {
  if (!strategy?.signals?.length) return null;

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-8">
      <h2 className="text-xl font-semibold mb-4">Advanced DCA Strategy</h2>
      
      <div className="space-y-2">
        {strategy.signals.map((signal, index) => (
          <div key={index} className="flex justify-between items-center py-1">
            <div>
              <div className="flex flex-col">
                <span>Price: ${formatPrice(signal.price)}</span>
                <span className="text-sm text-gray-500">Position Size: ${formatPrice(signal.position_size)}</span>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-medium">
                Strength: {formatPercentage(signal.signal_strength)}
              </span>
              <div className="w-16 bg-gray-200 rounded-full h-1">
                <div 
                  className="bg-green-500 h-1 rounded-full"
                  style={{ width: `${signal.signal_strength * 100}%` }}
                />
              </div>
            </div>
          </div>
        ))}
        <div className="text-sm text-gray-500 mt-4 pt-3 border-t">
          Total Investment: ${formatPrice(investmentAmount)}
        </div>
      </div>
    </div>
  );
}; 