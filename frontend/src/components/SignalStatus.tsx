import React from 'react';
import { TechnicalAnalysis } from '../types/analysis';
import { formatPrice } from '../utils/format';

interface SignalStatusProps {
  analysis: TechnicalAnalysis;
  currentPrice: number;
}

// New InfoIcon component for tooltips.
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

export const SignalStatus: React.FC<SignalStatusProps> = ({ analysis, currentPrice }) => {
  if (!analysis?.advanced_indicators) return null;

  const { advanced_indicators: ai } = analysis;

  // Define "good" conditions for a buying signal:
  const isRSIGood = (ai.rsi || 0) <= 70; // Good when RSI is 70 or below (i.e. not overbought)
  const isMACDGood = (ai.macd?.line || 0) > (ai.macd?.signal || 0);
  const isBBGood = ai.bollinger_bands && currentPrice < (ai.bollinger_bands.lower || 0);
  const isMAGood = (ai.sma_50 || 0) > currentPrice;

  const allGreen = isRSIGood && isMACDGood && isBBGood && isMAGood;

  const calculatePercentage = (level: number) => ((level - currentPrice) / currentPrice) * 100;

  return (
    <>
      <div className="bg-white p-6 rounded-lg shadow mb-8 relative">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold mb-4">Signal Status</h2>
          {allGreen && (
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-500 rounded-full" />
              <span className="text-green-500 font-bold">Green light for buying</span>
            </div>
          )}
        </div>
        {/* Indicator Signals Section */}
        <div className="space-y-4">
          <h3 className="font-medium">Indicator Signals</h3>
          <div className="grid grid-cols-2 gap-4">
            {/* RSI Overbought Signal */}
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isRSIGood ? 'bg-green-500' : 'bg-red-500'}`} />
              <span>RSI Overbought</span>
              <InfoIcon text={`RSI value: ${ai.rsi || 0}. Good when ≤ 70.`} />
            </div>
            {/* MACD Bullish Signal */}
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isMACDGood ? 'bg-green-500' : 'bg-red-500'}`} />
              <span>MACD Bullish</span>
              <InfoIcon text={`MACD Line: ${ai.macd?.line || 0}, Signal: ${ai.macd?.signal || 0}. Good when Line > Signal.`} />
            </div>
            {/* Below BB Signal */}
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isBBGood ? 'bg-green-500' : 'bg-red-500'}`} />
              <span>Below BB</span>
              <InfoIcon text={`Current Price: $${formatPrice(currentPrice)}, Lower BB: $${ai.bollinger_bands?.lower ? formatPrice(ai.bollinger_bands.lower) : 'N/A'}. Good when price < Lower BB.`} />
            </div>
            {/* MA Bullish Signal */}
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isMAGood ? 'bg-green-500' : 'bg-red-500'}`} />
              <span>MA Bullish</span>
              <InfoIcon text={`SMA 50: $${formatPrice(ai.sma_50 || 0)}, Current Price: $${formatPrice(currentPrice)}. Good when SMA 50 > Current Price.`} />
            </div>
          </div>
        </div>
      </div>

      {analysis.support_levels &&
       analysis.resistance_levels &&
       analysis.support_levels.length > 0 &&
       analysis.resistance_levels.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-semibold mb-4">Technical Levels</h2>
          <div className="grid grid-cols-2 gap-6">
            {/* Support Levels */}
            <div>
              <h4 className="font-medium mb-3">Support Levels</h4>
              <div className="space-y-2">
                {analysis.support_levels.map((level, index) => {
                  const percentage = calculatePercentage(level);
                  return (
                    <div
                      key={index}
                      className="flex justify-between items-center text-green-600 font-medium"
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
              <h4 className="font-medium mb-3">Resistance Levels</h4>
              <div className="space-y-2">
                {analysis.resistance_levels.map((level, index) => {
                  const percentage = calculatePercentage(level);
                  return (
                    <div
                      key={index}
                      className="flex justify-between items-center text-red-600 font-medium"
                    >
                      <span>${formatPrice(level)}</span>
                      <span>{percentage >= 0 ? '+' : ''}{percentage.toFixed(2)}%</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}; 
