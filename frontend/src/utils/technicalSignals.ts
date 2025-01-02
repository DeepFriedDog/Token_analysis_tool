import { TechnicalAnalysis } from '../types/analysis';

export const getTechnicalSignals = (analysis: TechnicalAnalysis, currentPrice: number) => {
  const { advanced_indicators: ai } = analysis;
  
  return {
    macd_signal: ai.macd.line > ai.macd.signal ? 'buy' : ai.macd.line < ai.macd.signal ? 'sell' : 'neutral',
    rsi_signal: ai.rsi >= 70 ? 'overbought' : ai.rsi <= 30 ? 'oversold' : 'neutral',
    bb_signal: currentPrice > ai.bollinger_bands.upper ? 'upper_break' : 
               currentPrice < ai.bollinger_bands.lower ? 'lower_break' : 'neutral'
  };
}; 