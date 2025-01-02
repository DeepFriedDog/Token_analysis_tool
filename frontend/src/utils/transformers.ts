import { TechnicalAnalysis } from '../types/analysis';
import { getTechnicalSignals } from './technicalSignals';

export const transformDCARecommendations = (
  analysis: TechnicalAnalysis,
  currentPrice: number,
  investmentAmount: number
) => {
  if (!analysis?.dca_recommendations?.entry_zones) {
    return {
      entry_points: [],
      exit_points: [],
      risk_score: 0,
      expected_return: 0,
      investment_distribution: []
    };
  }

  const { dca_recommendations } = analysis;
  
  return {
    entry_points: dca_recommendations.entry_zones.map(zone => ({
      price_level: zone.price_level,
      allocation: zone.allocation * investmentAmount,
      confidence: zone.confidence
    })),
    exit_points: analysis.exit_signals?.map(signal => ({
      price: signal.price,
      type: signal.type,
      confidence: signal.confidence,
      position_size: signal.confidence * investmentAmount
    })) || [],
    risk_score: dca_recommendations.risk_assessment.overall_risk,
    expected_return: 0,
    investment_distribution: dca_recommendations.entry_zones.map(zone => ({
      amount: zone.allocation * investmentAmount,
      price_target: zone.price_level
    }))
  };
};

export const transformAdvancedDCAStrategy = (
  analysis: TechnicalAnalysis,
  investmentAmount: number
) => {
  const { dca_recommendations } = analysis;
  const signals = getTechnicalSignals(analysis, 0);
  
  return {
    signals: dca_recommendations.entry_zones.map(zone => ({
      price: zone.price_level,
      signal_strength: zone.confidence,
      position_size: zone.allocation * investmentAmount,
      reasoning: zone.reasoning || []
    })),
    total_investment: investmentAmount,
    indicator_signals: {
      macd: signals.macd_signal,
      bb: signals.bb_signal
    }
  };
}; 