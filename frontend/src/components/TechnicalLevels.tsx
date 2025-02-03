import React from 'react';
import { formatPrice } from '../utils/format';

interface TechnicalLevelsProps {
  supportLevels: number[];
  resistanceLevels: number[];
  currentPrice: number;
}

export const TechnicalLevels: React.FC<TechnicalLevelsProps> = ({
  supportLevels,
  resistanceLevels,
  currentPrice
}) => {
  const calculatePercentage = (level: number) => {
    return ((level - currentPrice) / currentPrice) * 100;
  };

  const isNearby = (percentage: number) => Math.abs(percentage) <= 5;

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-8">
      <h2 className="text-xl font-semibold mb-4">Technical Levels</h2>
      <div className="grid grid-cols-2 gap-6">
        {/* Support Levels */}
        <div>
          <h3 className="font-medium mb-3">Support Levels</h3>
          <div className="space-y-2">
            {supportLevels.map((level, index) => {
              const percentage = calculatePercentage(level);
              return (
                <div 
                  key={index} 
                  className={`flex justify-between items-center ${
                    isNearby(percentage) ? 'text-green-600 font-medium' : ''
                  }`}
                >
                  <span>${formatPrice(level)}</span>
                  <span>{percentage.toFixed(2)}%</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Resistance Levels */}
        <div>
          <h3 className="font-medium mb-3">Resistance Levels</h3>
          <div className="space-y-2">
            {resistanceLevels.map((level, index) => {
              const percentage = calculatePercentage(level);
              return (
                <div 
                  key={index} 
                  className={`flex justify-between items-center ${
                    isNearby(percentage) ? 'text-red-600 font-medium' : ''
                  }`}
                >
                  <span>${formatPrice(level)}</span>
                  <span>+{percentage.toFixed(2)}%</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};