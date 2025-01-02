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
  technical_analysis: {
    trend_analysis: {
      primary_trend: string;
      strength: number;
    };
    dca_recommendations: {
      entry_zones: Array<{
        price_level: number;
        confidence: number;
        allocation: number;
      }>;
      risk_assessment: {
        overall_risk: number;
        key_risks: string[];
      };
    };
  };
}

export type { SentimentAnalysis, SentimentAnalysisParams } from './sentiment'; 