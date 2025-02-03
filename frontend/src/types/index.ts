import { TechnicalAnalysis } from './analysis';

export interface AnalysisParams {
  contractAddress: string;
  timeframe: string;
  intervalDays: number;
  investmentAmount: number;
}

export interface AnalysisResult {
  priceData: {
    current_price: number;
    price_history: Array<{
      timestamp: number;
      price: number;
      high: number;
      low: number;
    }>;
  };
  technical_analysis: TechnicalAnalysis;
}

export type { SentimentAnalysis, SentimentAnalysisParams } from './sentiment';

// Re-export ChartPriceData from analysis.ts
export type { ChartPriceData } from './analysis'; 