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
  const { support_levels, resistance_levels, advanced_indicators } = analysis;
  const fibonacci_levels = advanced_indicators?.fibonacci_levels;
  const signals = getTechnicalSignals(analysis, 0);
  const currentPrice = Number(advanced_indicators?.sma_50) || 
                      Number(advanced_indicators?.ema_50) || 
                      Number(support_levels?.[0]) || 0;
  
  // Combine support levels and Fibonacci support levels
  const allSupportLevels = [...(support_levels || [])];
  
  // Add Fibonacci support levels
  if (fibonacci_levels) {
    const fibSupports = fibonacci_levels
      .filter((level: { label?: string; price?: number }) => level.price !== undefined && level.price < currentPrice)
      .map((level: { label?: string; price?: number }) => level.price!);
    allSupportLevels.push(...fibSupports);
  }

  // Add BB lower band as potential support
  if (advanced_indicators?.bollinger_bands?.lower) {
    allSupportLevels.push(advanced_indicators.bollinger_bands.lower);
  }

  const validSupportLevels = Array.from(new Set(allSupportLevels))
    .filter(level => level < currentPrice)
    .sort((a, b) => b - a);

  const entry_strategy = validSupportLevels.length ? validSupportLevels.map(level => {
    const priceDiff = Math.abs(currentPrice - level);
    const weight = priceDiff / validSupportLevels.reduce((sum, l) => sum + Math.abs(currentPrice - l), 0);
    
    // Calculate confidence based on multiple factors
    let confidence = weight;
    if (level === advanced_indicators?.bollinger_bands?.lower) {
      confidence *= 1.2; // Boost confidence for BB support
    }
    if (fibonacci_levels?.some((fib: { label?: string; price?: number }) => fib.price === level)) {
      confidence *= 1.3; // Boost confidence for Fibonacci levels
    }
    
    const allocation = investmentAmount * confidence;
    
    return {
      entry_price: level,
      allocation: allocation,
      reasoning: [
        `Technical support level at ${level}`,
        ...(level === advanced_indicators?.bollinger_bands?.lower ? ['Bollinger Band support'] : []),
        ...(fibonacci_levels?.some((fib: { label?: string; price?: number }) => fib.price === level) ? ['Fibonacci support level'] : [])
      ]
    };
  }) : [{
    entry_price: currentPrice * 0.95,
    allocation: investmentAmount,
    reasoning: ['Default entry point at 5% below current price']
  }];

  // Calculate exit price from resistance levels
  const validResistance = (resistance_levels || [])
    .filter(level => level > currentPrice)
    .sort((a, b) => a - b)[0] || currentPrice * 1.2;

  const dca_strategy = {
    entry_strategy,
    exit_strategy: {
      exit_price: validResistance,
      sell_percentage: 100
    }
  };

  return {
    signals: entry_strategy.map((entry, index) => ({
      price: entry.entry_price,
      signal_strength: 1 - (index / entry_strategy.length),
      position_size: entry.allocation,
      reasoning: entry.reasoning
    })),
    total_investment: investmentAmount,
    dca_strategy
  };
}; 