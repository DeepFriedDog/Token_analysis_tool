import { PriceData } from './price';

interface AdvancedIndicators {
  macd?: {
    line: number;
    signal: number;
    histogram: number;
  };
  rsi?: number;
  bollinger_bands?: {
    upper: number;
    middle: number;
    lower: number;
  };
  volatility?: number;
  sma_50?: number;
  ema_50?: number;
}

export interface TechnicalAnalysis {
  trend_analysis: {
    primary_trend: 'bullish' | 'bearish' | 'neutral';
    strength: number;
  };
  dca_recommendations: {
    entry_zones: Array<{
      price_level: number;
      allocation: number;
      confidence: number;
      reasoning?: string[];
    }>;
    risk_assessment: {
      overall_risk: number;
      key_risks?: string[];
    };
  };
  advanced_indicators: AdvancedIndicators;
  exit_signals?: Array<{
    price: number;
    type: 'stop_loss' | 'take_profit';
    confidence: number;
    reasoning?: string[];
  }>;
}

export interface AnalysisResult {
  priceData: PriceData;
  technical_analysis: TechnicalAnalysis;
} 