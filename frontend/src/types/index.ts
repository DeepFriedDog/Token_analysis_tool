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
      timestamp: string;
      price: number;
    }>;
  };
  technical_analysis: TechnicalAnalysis;
}

export type { SentimentAnalysis, SentimentAnalysisParams } from './sentiment'; 