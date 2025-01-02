import { TechnicalAnalysis } from '../types/analysis';

interface TechnicalSignals {
  dca_signal: 'buy' | 'sell' | 'neutral';
  macd_signal: 'buy' | 'sell' | 'neutral';
  rsi_signal: 'overbought' | 'oversold' | 'neutral';
  bb_signal: 'upper_break' | 'lower_break' | 'neutral';
}

export const getTechnicalSignals = (analysis: TechnicalAnalysis, currentPrice: number): TechnicalSignals => {
  const { advanced_indicators: ai } = analysis;
  
  if (!ai?.macd || !ai?.rsi || !ai?.bollinger_bands) {
    return {
      dca_signal: 'neutral',
      macd_signal: 'neutral',
      rsi_signal: 'neutral',
      bb_signal: 'neutral'
    };
  }

  // Calculate signals based on technical indicators
  const macd_signal = ai.macd.line > ai.macd.signal ? 'buy' : 
                     ai.macd.line < ai.macd.signal ? 'sell' : 'neutral';
                     
  const rsi_signal = ai.rsi >= 70 ? 'overbought' : 
                    ai.rsi <= 30 ? 'oversold' : 'neutral';
                    
  const bb_signal = currentPrice > ai.bollinger_bands.upper ? 'upper_break' : 
                   currentPrice < ai.bollinger_bands.lower ? 'lower_break' : 'neutral';

  // Calculate DCA signal based on multiple indicators
  const dca_signal = (
    macd_signal === 'buy' && 
    rsi_signal === 'oversold' && 
    bb_signal === 'lower_break'
  ) ? 'buy' : (
    macd_signal === 'sell' && 
    rsi_signal === 'overbought' && 
    bb_signal === 'upper_break'
  ) ? 'sell' : 'neutral';
  
  return {
    dca_signal,
    macd_signal,
    rsi_signal,
    bb_signal
  };
}; 