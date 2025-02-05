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
  sma_200?: number;
  ema_200?: number;
  fibonacci_levels?: Array<{ label?: string; price?: number }>;
}

export interface AdvancedDCAStrategy {
  entry_strategy: Array<{
    entry_price: number;
    allocation: number;
    reasoning?: string[];
  }>;
  exit_strategy: {
    sell_percentage: number;
    exit_price: number;
  };
}

export interface TechnicalAnalysis {
  trend_analysis: {
    primary_trend: 'bullish' | 'bearish' | 'neutral';
    strength: number;
  };
  support_levels: number[];
  resistance_levels: number[];
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
  dca_strategy?: AdvancedDCAStrategy;
}

export interface AnalysisResult {
  priceData: PriceData;
  technical_analysis: TechnicalAnalysis;
}

// Interface for price chart data points
export interface ChartPriceData {
  timestamp: number;
  price: number;
  high: number;
  low: number;
}

// New interface for DCA Strategy improvements
export interface DCAStrategy {
  signalStatus: string;        // e.g. 'Buy', 'Sell', 'Neutral'
  suggestedPositions: number[];  // Array of suggested entry positions
} 