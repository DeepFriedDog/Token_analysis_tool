import React from 'react';
import { formatPrice, formatPercentage } from '../utils/format';

interface EntryPoint {
  price_level: number;
  allocation: number;
  confidence: number;
}

interface Props {
  entryPoints: EntryPoint[];
  currentPrice: number;
}

const DCAStrategySection: React.FC<Props> = ({ entryPoints, currentPrice }) => {
  const totalAllocation = entryPoints.reduce((sum, point) => sum + point.allocation, 0);

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-8">
      <h2 className="text-xl font-semibold mb-4">DCA Strategy</h2>
      <div className="space-y-2">
        {entryPoints.map((point, index) => {
          const percentDiff = ((point.price_level - currentPrice) / currentPrice) * 100;
          const diffColor = percentDiff >= 0 ? 'text-green-600' : 'text-red-600';
          return (
            <div key={index} className="flex justify-between items-center py-2">
              <span>Entry Price: ${formatPrice(point.price_level)}</span>
              <span className={diffColor}>
                ({percentDiff >= 0 ? '+' : ''}{formatPercentage(percentDiff)})
              </span>
              <span>Order Size: ${formatPrice(point.allocation)}</span>
            </div>
          );
        })}
      </div>
      <div className="mt-4 text-sm text-gray-500">
        Total Investment: ${formatPrice(totalAllocation)}
      </div>
    </div>
  );
};

export default DCAStrategySection; 