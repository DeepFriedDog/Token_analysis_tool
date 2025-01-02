import React from 'react';
import type { AdvancedDCAStrategy as AdvancedDCAStrategyType } from '../types/analysis';
import { formatPrice, formatPercentage } from '../utils/formatters';

interface Props {
  strategy: AdvancedDCAStrategyType;
  investmentAmount: number;
}

export const AdvancedDCAStrategy: React.FC<Props> = ({ strategy, investmentAmount }) => {
  if (!strategy || !strategy.indicator_signals) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Advanced DCA Strategy</h2>
        <p className="text-gray-500">No strategy data available</p>
      </div>
    );
  }

  // Calculate adjusted position sizes based on signal strength
  const totalSignalStrength = strategy.signals?.reduce((sum, signal) => sum + signal.signal_strength, 0) || 1;
  const adjustedSignals = strategy.signals?.map(signal => ({
    ...signal,
    position_size: Number(((investmentAmount * signal.signal_strength) / totalSignalStrength).toFixed(2))
  }));

  // Ensure total matches investment amount exactly by adjusting last position
  if (adjustedSignals && adjustedSignals.length > 0) {
    const currentTotal = adjustedSignals.reduce((sum, signal) => sum + signal.position_size, 0);
    const difference = investmentAmount - currentTotal;
    adjustedSignals[adjustedSignals.length - 1].position_size += Number(difference.toFixed(2));
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">Advanced DCA Strategy</h2>
      
      {/* Entry Signals */}
      {adjustedSignals && adjustedSignals.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-2">Entry Signals</h3>
          <div className="space-y-2">
            {adjustedSignals.map((signal, index) => (
              <div key={index} className="border rounded p-3">
                <div className="flex justify-between mb-2">
                  <span>Price: ${formatPrice(signal.price)}</span>
                  <span className="font-semibold">
                    Strength: {formatPercentage(signal.signal_strength)}
                  </span>
                </div>
                <div className="text-sm text-gray-600">
                  Position Size: ${signal.position_size}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-3 text-sm text-gray-500">
            Total Investment: ${investmentAmount}
          </div>
        </div>
      )}
    </div>
  );
}; 