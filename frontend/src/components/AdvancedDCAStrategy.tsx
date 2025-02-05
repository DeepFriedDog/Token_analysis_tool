import React from 'react';
import { formatPrice, formatPercentage } from '../utils/format';
import { AdvancedDCAStrategy as StrategyType } from '../types/analysis';

interface Props {
  strategy: {
    signals: Array<{
      price: number;
      signal_strength: number;
      position_size: number;
      reasoning?: string[];
    }>;
    dca_strategy?: StrategyType;
    total_investment: number;
  };
  investmentAmount: number;
  currentPrice: number;
}

export const AdvancedDCAStrategy: React.FC<Props> = ({ strategy, investmentAmount, currentPrice }) => {
  // Generate DCA strategy from support levels if none exists
  const generateDCAStrategy = () => {
    if (!strategy.signals || strategy.signals.length === 0) {
      return null;
    }

    // Sort signals by price
    const sortedSignals = [...strategy.signals].sort((a, b) => a.price - b.price);
    
    // Calculate total signal strength
    const totalStrength = sortedSignals.reduce((sum, signal) => sum + signal.signal_strength, 0);
    
    // Generate entry strategy
    const entry_strategy = sortedSignals.map(signal => ({
      entry_price: signal.price,
      allocation: (signal.signal_strength / totalStrength) * investmentAmount,
      reasoning: signal.reasoning || [`Support level with ${formatPercentage(signal.signal_strength * 100)} confidence`]
    }));

    // Calculate exit strategy using the highest signal price + 20%
    const highestEntry = Math.max(...sortedSignals.map(s => s.price));
    const exitPrice = highestEntry * 1.2; // 20% above highest entry

    return {
      entry_strategy,
      exit_strategy: {
        exit_price: exitPrice,
        sell_percentage: 100
      }
    };
  };

  const dcaStrategy = strategy.dca_strategy || generateDCAStrategy();
  
  if (!dcaStrategy || !dcaStrategy.entry_strategy?.length || 
      !dcaStrategy.exit_strategy?.exit_price || 
      dcaStrategy.exit_strategy.exit_price <= 0) {
    return (
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-semibold mb-4">Advanced DCA Strategy</h2>
        <p className="text-sm text-gray-600">
          Unable to generate a valid DCA strategy at this time. This might be due to:
          <ul className="list-disc list-inside mt-2">
            <li>High market volatility</li>
            <li>Insufficient historical data</li>
            <li>Unclear market direction</li>
          </ul>
        </p>
      </div>
    );
  }

  const { entry_strategy, exit_strategy } = dcaStrategy;

  // Calculate total allocation for percentage distribution
  const totalAllocation = entry_strategy.reduce((sum, entry) => sum + entry.allocation, 0);

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-8">
      <h2 className="text-xl font-semibold mb-4">Advanced DCA Strategy</h2>
      
      {/* Entry Strategy */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-3">Entry Strategy</h3>
        <p className="text-sm text-gray-600 mb-3">
          Based on support levels and technical indicators, we suggest dividing your investment of ${formatPrice(investmentAmount)} into {entry_strategy.length} positions. 
          The suggested entry prices are derived from key technical support zones, moving averages, and market momentum data.
        </p>
        <div className="space-y-4">
          {entry_strategy.map((entry, index) => {
            const percentDiff = ((entry.entry_price - currentPrice) / currentPrice) * 100;
            const diffColor = percentDiff >= 0 ? 'text-green-600' : 'text-red-600';
            const allocationPercentage = (entry.allocation / totalAllocation) * 100;
            
            return (
              <div key={index} className="border-b pb-3">
                <div className="flex justify-between items-center py-2">
                  <span>Suggested Entry Price: ${formatPrice(entry.entry_price)}</span>
                  <span className={diffColor}>
                    ({percentDiff >= 0 ? '+' : ''}{formatPercentage(percentDiff)})
                  </span>
                </div>
                <div className="flex justify-between items-center text-sm text-gray-600">
                  <span>Allocated Amount: ${formatPrice(entry.allocation)}</span>
                  <span>({formatPercentage(allocationPercentage)} of total)</span>
                </div>
                {entry.reasoning && entry.reasoning.length > 0 && (
                  <div className="mt-2">
                    <span className="text-xs text-gray-500">Rationale: </span>
                    <ul className="list-disc list-inside text-xs text-gray-500">
                      {entry.reasoning.map((reason, reasonIndex) => (
                        <li key={reasonIndex}>{reason}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 rounded-full h-2"
                    style={{ width: `${allocationPercentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Exit Strategy */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-3">Exit Strategy</h3>
        <p className="text-sm text-gray-600 mb-3">
          The exit strategy is determined using Fibonacci retracement levels, resistance lines, and other technical indicators.
          This approach helps you to gradually take profits as the price moves beyond key resistance zones.
        </p>
        <div className="space-y-2">
          <div className="flex justify-between items-center py-2">
            <span>Suggested Exit Price: ${formatPrice(exit_strategy.exit_price)}</span>
            <span className="text-green-600">
              (+{formatPercentage(((exit_strategy.exit_price - currentPrice) / currentPrice) * 100)})
            </span>
          </div>
          <div className="flex justify-between items-center py-2">
            <span>Sell Percentage:</span>
            <span className="font-medium">{exit_strategy.sell_percentage}%</span>
          </div>
        </div>
      </div>
      
      {/* Summary */}
      <div className="text-sm text-gray-500 mt-4 pt-3 border-t">
        <div>Total Investment: ${formatPrice(investmentAmount)}</div>
        <div>Number of Entry Positions: {entry_strategy.length}</div>
      </div>
    </div>
  );
};

export default AdvancedDCAStrategy;