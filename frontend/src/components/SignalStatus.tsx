import React from 'react';
import { TechnicalAnalysis } from '../types/analysis';

interface SignalStatusProps {
  analysis: TechnicalAnalysis;
  currentPrice: number;
}

export const SignalStatus: React.FC<SignalStatusProps> = ({ analysis, currentPrice }) => {
  if (!analysis?.advanced_indicators) return null;

  const { advanced_indicators: ai } = analysis;
  const rsiOverbought = (ai.rsi || 0) > 70;
  const macdBullish = (ai.macd?.line || 0) > (ai.macd?.signal || 0);
  const belowBB = ai.bollinger_bands && currentPrice < (ai.bollinger_bands.lower || 0);
  const maBullish = (ai.sma_50 || 0) > currentPrice;

  return (
    <div className="bg-white p-6 rounded-lg shadow mb-8">
      <h2 className="text-xl font-semibold mb-4">DCA Strategy</h2>
      
      <div className="space-y-4">
        <h3 className="font-medium">Signal Status</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${rsiOverbought ? 'bg-red-500' : 'bg-gray-300'}`} />
            <span>RSI Overbought</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${macdBullish ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span>MACD Bullish</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${belowBB ? 'bg-red-500' : 'bg-gray-300'}`} />
            <span>Below BB</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${maBullish ? 'bg-green-500' : 'bg-gray-300'}`} />
            <span>MA Bullish</span>
          </div>
        </div>
      </div>
    </div>
  );
}; 
