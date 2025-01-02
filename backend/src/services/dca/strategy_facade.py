from decimal import Decimal
from typing import Dict, List, Optional
import pandas as pd
from .calculator import DCACalculator
from .advanced_calculator import AdvancedDCACalculator

class DCAStrategyFacade:
    def __init__(self, price_data: pd.DataFrame, investment_amount: Decimal, risk_tolerance: Optional[Decimal] = None):
        self.price_data = price_data
        self.investment_amount = investment_amount
        self.risk_tolerance = risk_tolerance or Decimal('0.5')
        self.basic_calculator = DCACalculator(price_data, investment_amount)
        self.advanced_calculator = AdvancedDCACalculator(price_data, investment_amount, self.risk_tolerance)

    def get_analysis_result(self, support_levels: List[float], resistance_levels: List[float], fibonacci_levels: List[Dict]) -> Dict:
        """Get complete analysis result in the format expected by frontend"""
        # Get basic DCA strategy
        basic_strategy = self.basic_calculator.calculate_entry_points(support_levels, resistance_levels)
        exit_points = self.basic_calculator.calculate_exit_points(resistance_levels, fibonacci_levels)
        
        # Get advanced DCA strategy
        advanced_signals = self.advanced_calculator.calculate_entry_signals()
        latest_indicators = self.advanced_calculator.get_latest_indicator_signals()
        
        # Format price data according to PriceData interface
        price_data = [
            {
                'timestamp': str(timestamp),
                'close': float(row['close'])
            }
            for timestamp, row in self.price_data.iterrows()
        ]
        
        # Get advanced indicators
        advanced_indicators = self._get_advanced_indicators()
        
        return {
            "priceData": price_data,
            "technical_analysis": {
                "support_levels": support_levels,
                "resistance_levels": resistance_levels,
                "fibonacci_levels": fibonacci_levels,
                "rsi": float(advanced_indicators["rsi"]),
                "volatility": float(self.basic_calculator.calculate_volatility()),
                "advanced_indicators": advanced_indicators
            },
            "dca_strategy": {
                "signals": advanced_signals,
                "risk_tolerance": float(self.risk_tolerance),
                "expected_return": 0.0,
                "position_sizes": [
                    {
                        "price_target": float(point["price"]),
                        "amount": float(point["position_size"]),
                        "signal_strength": float(point.get("strength", 0.5))
                    }
                    for point in basic_strategy
                ],
                "indicator_signals": latest_indicators,
                "entry_points": [
                    {
                        "price": float(point["price"]),
                        "percentage": float(point["percentage"])
                    }
                    for point in basic_strategy
                ],
                "exit_points": [
                    {
                        "price": float(point["price"]),
                        "percentage": float(point["percentage"])
                    }
                    for point in exit_points
                ]
            }
        }

    def _get_advanced_indicators(self) -> Dict:
        """Get the latest advanced indicators"""
        indicators = self.advanced_calculator.indicators
        latest_idx = -1
        
        return {
            "sma_20": float(indicators['sma_50'].iloc[latest_idx]),
            "sma_50": float(indicators['sma_50'].iloc[latest_idx]),
            "ema_20": float(indicators['ema_20'].iloc[latest_idx]),
            "rsi": float(indicators['rsi'].iloc[latest_idx]),
            "macd": {
                "line": float(indicators['macd'].iloc[latest_idx]),
                "signal": float(indicators['macd_signal'].iloc[latest_idx]),
                "histogram": float(indicators['macd'].iloc[latest_idx] - indicators['macd_signal'].iloc[latest_idx])
            },
            "bollinger_bands": {
                "upper": float(indicators['bbands']['upper'].iloc[latest_idx]),
                "middle": float(indicators['bbands']['middle'].iloc[latest_idx]),
                "lower": float(indicators['bbands']['lower'].iloc[latest_idx])
            },
            "mfi": 50.0  # You'll need to implement MFI calculation if needed
        } 