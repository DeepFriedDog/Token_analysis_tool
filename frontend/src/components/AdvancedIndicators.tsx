import React from 'react';
import { formatPrice } from '../utils/format';
import { TechnicalAnalysis } from '../types/analysis';

interface AdvancedIndicatorsProps {
  analysis: TechnicalAnalysis;
}

export const AdvancedIndicators: React.FC<AdvancedIndicatorsProps> = ({ analysis }) => {
  if (!analysis) return null;
  
  const { advanced_indicators: ai } = analysis;

  if (!ai) return null;

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-4">
      <h3 className="text-xl font-semibold mb-4">Advanced Technical Analysis</h3>
      
      {/* Moving Averages */}
      <div className="mb-6">
        <h4 className="text-lg font-medium mb-3">Moving Averages</h4>
        <div className="flex justify-between">
          <span className="text-gray-600">SMA 50</span>
          <span>${formatPrice(ai.sma_50 ?? 0)}</span>
        </div>
      </div>

      {/* MACD */}
      <div className="mb-6">
        <h4 className="text-lg font-medium mb-3">MACD</h4>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-gray-600">Line</span>
            <span className="text-red-500">${formatPrice(ai.macd?.line ?? 0)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Signal</span>
            <span>${formatPrice(ai.macd?.signal ?? 0)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Histogram</span>
            <span>${formatPrice(ai.macd?.histogram ?? 0)}</span>
          </div>
        </div>
      </div>

      {/* Bollinger Bands */}
      <div>
        <h4 className="text-lg font-medium mb-3">Bollinger Bands</h4>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span className="text-gray-600">Upper Band</span>
            <span>${formatPrice(ai.bollinger_bands?.upper ?? 0)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Middle Band</span>
            <span>${formatPrice(ai.bollinger_bands?.middle ?? 0)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Lower Band</span>
            <span>${formatPrice(ai.bollinger_bands?.lower ?? 0)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}; 