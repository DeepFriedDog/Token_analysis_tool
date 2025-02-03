import React from 'react';
import { TechnicalAnalysis } from '../types/analysis';

interface AdvancedIndicatorsProps {
  analysis: TechnicalAnalysis;
  currentPrice: number;
}

// Local InfoIcon component for tooltips.
const InfoIcon: React.FC<{ text: string }> = ({ text }) => (
  <div className="relative group inline-block">
    <span className="ml-1 text-xs text-gray-500 cursor-pointer rounded-full border border-gray-400 w-4 h-4 flex items-center justify-center">
      ?
    </span>
    <div className="absolute bottom-full mb-2 left-1/2 transform -translate-x-1/2 hidden group-hover:block bg-black text-white text-xs rounded py-1 px-2 z-10 whitespace-nowrap">
      {text}
    </div>
  </div>
);

// Helper function to display moving average value or "N/A" with 8 decimals
const displayMA = (value?: number) => {
  return value != null ? '$' + Number(value).toFixed(8) : 'N/A';
};

export const AdvancedIndicators: React.FC<AdvancedIndicatorsProps> = ({ analysis, currentPrice }) => {
  if (!analysis) return null;
  
  const { advanced_indicators: ai } = analysis;
  if (!ai) return null;

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-4">
      <h3 className="text-xl font-semibold mb-4">Advanced Technical Analysis</h3>
      
      {/* Moving Averages */}
      <div className="mb-6">
        <h4 className="text-lg font-medium mb-3">Moving Averages</h4>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">
              SMA 50 
              <InfoIcon text="Simple Moving Average computed as the average of the closing prices from the last available 50 data points. (If fewer than 50 exist, all available data is used.)" />
            </span>
            <span>{displayMA(ai.sma_50)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">
              EMA 50 
              <InfoIcon text="Exponential Moving Average computed over the entire series starting from the first available price, using a 50-period smoothing factor." />
            </span>
            <span>{displayMA(ai.ema_50)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">
              SMA 200 
              <InfoIcon text="Simple Moving Average computed as the average of the closing prices from the last available 200 data points. (If fewer than 200 exist, all available data is used.)" />
            </span>
            <span>{displayMA(ai.sma_200)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">
              EMA 200 
              <InfoIcon text="Exponential Moving Average computed over the entire series starting from the first available price, using a 200-period smoothing factor." />
            </span>
            <span>{displayMA(ai.ema_200)}</span>
          </div>
        </div>
      </div>

      {/* MACD */}
      <div className="mb-6">
        <h4 className="text-lg font-medium mb-3">MACD</h4>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">
              Line 
              <InfoIcon text="MACD Line: Difference between the 12-period EMA and the 26-period EMA, indicating trend momentum." />
            </span>
            <span>{ai.macd?.line !== undefined ? Number(ai.macd.line).toFixed(8) : 'N/A'}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">
              Signal 
              <InfoIcon text="Signal Line: 9-period EMA of the MACD Line, used for buy/sell signals." />
            </span>
            <span>{ai.macd?.signal !== undefined ? Number(ai.macd.signal).toFixed(8) : 'N/A'}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">
              Histogram 
              <InfoIcon text="Histogram: Difference between the MACD Line and the Signal Line, illustrating momentum changes." />
            </span>
            <span>{ai.macd?.histogram !== undefined ? Number(ai.macd.histogram).toFixed(8) : 'N/A'}</span>
          </div>
        </div>
      </div>

      {/* Bollinger Bands */}
      <div>
        <h4 className="text-lg font-medium mb-3">Bollinger Bands</h4>
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-gray-600">
              Upper Band 
              <InfoIcon text="Upper Band: Typically calculated as the SMA plus a multiple of the standard deviation." />
            </span>
            <span>${Number(ai.bollinger_bands?.upper ?? 0).toFixed(8)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">
              Middle Band 
              <InfoIcon text="Middle Band: Usually the SMA over the period." />
            </span>
            <span>${Number(ai.bollinger_bands?.middle ?? 0).toFixed(8)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-gray-600">
              Lower Band 
              <InfoIcon text="Lower Band: Typically calculated as the SMA minus a multiple of the standard deviation." />
            </span>
            <span>${Number(ai.bollinger_bands?.lower ?? 0).toFixed(8)}</span>
          </div>
        </div>
      </div>

      {/* Fibonacci Analysis */}
      <div className="mt-6">
        <h4 className="text-lg font-medium mb-3">
          Fibonacci Analysis
          <InfoIcon text="Key price levels where the asset might reverse direction. Green levels indicate potential buy zones, red levels show possible resistance." />
        </h4>
        <div className="space-y-2">
          {ai.fibonacci_levels && ai.fibonacci_levels.length > 0 ? (
            ai.fibonacci_levels.map((level: { label?: string; price?: number; level?: number }, index: number) => {
              const priceDiff = ((level.price! - currentPrice) / currentPrice) * 100;
              const isSupport = level.price! < currentPrice;
              
              return (
                <div key={index} className="flex justify-between items-center">
                  <span className={`${isSupport ? 'text-green-600' : 'text-red-600'} flex items-center gap-2`}>
                    {level.label}
                    {Math.abs(priceDiff) < 5 && 
                      <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">Near</span>
                    }
                  </span>
                  <div className="flex flex-col items-end">
                    <span className="font-medium">${level.price ? Number(level.price).toFixed(8) : 'N/A'}</span>
                    <span className={`text-xs ${isSupport ? 'text-green-600' : 'text-red-600'}`}>
                      {priceDiff > 0 ? '+' : ''}{priceDiff.toFixed(2)}%
                    </span>
                  </div>
                </div>
              );
            })
          ) : (
            <div>No Fibonacci data available</div>
          )}
        </div>
      </div>
    </div>
  );
};