import { ChartPriceData } from '../types/price';

export const calculateMovingAverages = (priceData: ChartPriceData) => {
  const prices = priceData.price_history.map(p => p.price);
  
  const calculateSMA = (period: number) => {
    if (prices.length === 0) return 0;
    const actualPeriod = Math.min(prices.length, period);
    const sum = prices.slice(-actualPeriod).reduce((a, b) => a + b, 0);
    return sum / actualPeriod;
  };

  const calculateEMA = (period: number) => {
    if (prices.length === 0) return 0;
    const multiplier = 2 / (period + 1);
    // Use the first price as the initial EMA
    let ema = prices[0];
    for (let i = 1; i < prices.length; i++) {
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