import { TechnicalAnalysis } from './analysis';

export interface PricePoint {
  timestamp: number;
  value: number;
  formatted: {
    price: string;
    high: string;
    low: string;
  };
}

export interface PriceData {
  prices: PricePoint[];
  timeframe: string;
  interval_days: number;
}

export interface ChartPriceData {
  current_price: number;
  price_history: Array<{
    timestamp: number;
    price: number;
    high: number;
    low: number;
  }>;
}

export interface AnalysisResult {
  priceData: ChartPriceData;
  technical_analysis: TechnicalAnalysis;
} 