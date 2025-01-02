import React from 'react';
import { AdvancedIndicators } from '../types/analysis';
import { formatPrice } from '../utils/formatters';

interface Props {
  indicators: AdvancedIndicators;
  currentPrice: number;
}

export const AdvancedIndicatorsPanel: React.FC<Props> = ({ indicators, currentPrice }) => {
  // Early return if indicators are not available
  if (!indicators) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Advanced Technical Analysis</h2>
        <p className="text-gray-500">Loading indicators...</p>
      </div>
    );
  }

  const {
    sma_20 = 0,
    sma_50 = 0,
    ema_20 = 0,
    macd = { line: 0, signal: 0, histogram: 0 },
    bollinger_bands = { upper: 0, middle: 0, lower: 0 }
  } = indicators;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">Advanced Technical Analysis</h2>
      
      {/* Moving Averages */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Moving Averages</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <span className="text-gray-600">SMA 20</span>
            <div className={`font-semibold ${sma_20 && currentPrice > sma_20 ? 'text-green-500' : 'text-red-500'}`}>
              ${formatPrice(sma_20)}
            </div>
          </div>
          <div>
            <span className="text-gray-600">SMA 50</span>
            <div className={`font-semibold ${sma_50 && currentPrice > sma_50 ? 'text-green-500' : 'text-red-500'}`}>
              ${formatPrice(sma_50)}
            </div>
          </div>
        </div>
      </div>

      {/* MACD */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">MACD</h3>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Line</span>
            <span>${formatPrice(macd.line)}</span>
          </div>
          <div className="flex justify-between">
            <span>Signal</span>
            <span>${formatPrice(macd.signal)}</span>
          </div>
          <div className="flex justify-between">
            <span>Histogram</span>
            <span>${formatPrice(macd.histogram)}</span>
          </div>
        </div>
      </div>

      {/* Bollinger Bands */}
      <div>
        <h3 className="text-lg font-semibold mb-2">Bollinger Bands</h3>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Upper Band</span>
            <span>${formatPrice(bollinger_bands.upper)}</span>
          </div>
          <div className="flex justify-between">
            <span>Middle Band</span>
            <span>${formatPrice(bollinger_bands.middle)}</span>
          </div>
          <div className="flex justify-between">
            <span>Lower Band</span>
            <span>${formatPrice(bollinger_bands.lower)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}; 