export interface PriceData {
  timestamp: string;
  close: number;
  volume?: number;
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
  support_levels: number[];
  resistance_levels: number[];
  rsi: number;
  volatility: number;
  fibonacci_levels: Array<{
    level: number;
    price: number;
    type: string;
  }>;
  advanced_indicators: AdvancedIndicators;
  trend_analysis?: {
    primary_trend: 'bullish' | 'bearish' | 'neutral';
    strength: number;
    key_levels: {
      major_support: number;
      major_resistance: number;
      breakout_target: number;
      breakdown_target: number;
    };
  };
  dca_recommendations?: {
    entry_zones: Array<{
      price: number;
      strength: number;
      confidence: number;
      reasoning: string[];
    }>;
    risk_assessment: {
      overall_risk: number;
      key_risks: string[];
      mitigations: string[];
    };
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
  priceData: PriceData[];
  technical_analysis: TechnicalAnalysis & {
    advanced_indicators: AdvancedIndicators;
  };
  dca_strategy?: AdvancedDCAStrategy;
} 