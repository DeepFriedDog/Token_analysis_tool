import { ChartPriceData } from '../types/price';

export const calculateMovingAverages = (priceData: ChartPriceData) => {
  const prices = priceData.price_history.map(p => p.price);
  
  const calculateSMA = (period: number) => {
    if (prices.length < period) return 0;
    const sum = prices.slice(-period).reduce((a, b) => a + b, 0);
    return sum / period;
  };

  const calculateEMA = (period: number) => {
    if (prices.length < period) return 0;
    const multiplier = 2 / (period + 1);
    let ema = prices.slice(0, period).reduce((a, b) => a + b, 0) / period;
    
    for (let i = period; i < prices.length; i++) {
      ema = (prices[i] - ema) * multiplier + ema;
    }
    return ema;
  };

  return {
    sma_50: calculateSMA(50),
    ema_50: calculateEMA(50),
    sma_200: calculateSMA(200),
    ema_200: calculateEMA(200)
  };
}; 