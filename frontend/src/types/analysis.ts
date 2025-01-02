export interface PriceData {
  current_price: number;
  price_history: Array<{
    timestamp: string;
    price: number;
  }>;
}

export interface DCAStrategyData {
  entry_points: Array<{
    price: number;
    percentage: number;
    position_size?: number;
    strength?: number;
  }>;
  exit_points: Array<{ price: number; percentage: number }>;
  risk_score: number;
  expected_return: number;
  investment_distribution: Array<{
    amount: number;
    price_target: number;
  }>;
}

export interface TechnicalAnalysis {
  trend_analysis: {
    primary_trend: string;
    strength: number;
  };
  dca_recommendations: {
    entry_zones: Array<{
      price_level: number;
      confidence: number;
      allocation: number;
      reasoning?: string[];
    }>;
    risk_assessment: {
      overall_risk: number;
      key_risks: string[];
    };
  };
  support_levels: number[];
  resistance_levels: number[];
  rsi: number;
  volatility: number;
  macd: {
    line: number;
    signal: number;
    histogram: number;
  };
}

export interface AdvancedIndicators {
  sma_20: number;
  sma_50: number;
  ema_20: number;
  rsi: number;
  macd: {
    line: number;
    signal: number;
    histogram: number;
  };
  bollinger_bands: {
    upper: number;
    middle: number;
    lower: number;
  };
  mfi: number;
}

export interface DCASignal {
  price: number;
  timestamp: string;
  signal_strength: number;
  position_size: number;
  indicators: {
    rsi: number;
    macd_crossover: boolean;
    bb_position: number;
    trend_strength: number;
  };
}

export interface AdvancedDCAStrategy {
  signals: DCASignal[];
  risk_tolerance: number;
  expected_return: number;
  position_sizes: Array<{
    price_target: number;
    amount: number;
    signal_strength: number;
  }>;
  indicator_signals: {
    rsi_oversold: boolean;
    macd_bullish: boolean;
    bb_oversold: boolean;
    trend_following: boolean;
  };
  entry_points: Array<{ price: number; percentage: number }>;
  exit_points: Array<{ price: number; percentage: number }>;
}

export interface AnalysisResult {
  priceData: PriceData;
  technical_analysis: TechnicalAnalysis;
} 