import React from 'react';
import { formatPrice, formatPercentage } from '../utils/format';

interface EntryZone {
  price_level: number;
  allocation: number;
  confidence: number;
}

interface Props {
  zones: EntryZone[];
  currentPrice: number;
}

export const EntryZones: React.FC<Props> = ({ zones, currentPrice }) => {
  if (!zones?.length) return null;

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-8">
      <h2 className="text-xl font-semibold mb-4">Entry Points</h2>
      
      <div className="space-y-2">
        {zones.map((zone, index) => {
          const percentDiff = ((zone.price_level - currentPrice) / currentPrice) * 100;
          
          return (
            <div key={index} className="flex justify-between items-center py-2">
              <div>
                <span>Price: ${formatPrice(zone.price_level)}</span>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-gray-500">
                  ({percentDiff > 0 ? '+' : ''}{formatPercentage(percentDiff)})
                </span>
                <span className="text-gray-500">${formatPrice(zone.allocation)}</span>
                <div className="w-16 bg-gray-200 h-1 rounded-full">
                  <div 
                    className="bg-green-500 h-1 rounded-full" 
                    style={{ width: `${zone.confidence * 100}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}; 