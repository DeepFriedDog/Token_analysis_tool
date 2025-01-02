import React from 'react';
import { formatPrice } from '../utils/format';
import { TechnicalAnalysis } from '../types/analysis';

interface TechnicalIndicatorsProps {
  analysis: TechnicalAnalysis;
  currentPrice: number;
}

export const TechnicalIndicators: React.FC<TechnicalIndicatorsProps> = ({ analysis, currentPrice }) => {
  if (!analysis?.advanced_indicators) return null;

  const { advanced_indicators: ai } = analysis;

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-8">
      <h2 className="text-xl font-semibold mb-4">Technical Indicators</h2>
      
      <div className="grid grid-cols-2 gap-6">
        {/* MACD Section */}
        <div className="bg-gray-50 p-4 rounded">
          <h3 className="font-medium mb-3">MACD</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Line:</span>
              <span>${formatPrice(ai.macd?.line || 0)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Signal:</span>
              <span>${formatPrice(ai.macd?.signal || 0)}</span>
            </div>
          </div>
        </div>

        {/* Bollinger Bands Section */}
        <div className="bg-gray-50 p-4 rounded">
          <h3 className="font-medium mb-3">Bollinger Bands</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Upper:</span>
              <span>${formatPrice(ai.bollinger_bands?.upper || 0)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Lower:</span>
              <span>${formatPrice(ai.bollinger_bands?.lower || 0)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 