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
        """Get complete analysis result with preserved precision"""
        price_data = [
            {
                'timestamp': str(timestamp),
                'close': str(row['close']),  # Convert Decimal to string to preserve precision
                'high': str(row.get('high', row['close'])),
                'low': str(row.get('low', row['close']))
            }
            for timestamp, row in self.price_data.iterrows()
        ]
        
        return {
            "priceData": price_data,
            "technical_analysis": {
                "support_levels": [str(level) for level in support_levels],
                "resistance_levels": [str(level) for level in resistance_levels],
                "fibonacci_levels": [
                    {**level, 'price': str(level['price'])}
                    for level in fibonacci_levels
                ],
                "rsi": str(self.advanced_calculator.indicators['rsi'].iloc[-1]),
                "volatility": str(self.basic_calculator.calculate_volatility()),
                "advanced_indicators": self._get_advanced_indicators(as_string=True)
            }
        }

    def _get_advanced_indicators(self, as_string: bool = False) -> Dict:
        """Get the latest advanced indicators"""
        indicators = self.advanced_calculator.indicators
        latest_idx = -1
        
        result = {
            "sma_20": float(indicators['sma_50'].iloc[latest_idx]) if not as_string else str(float(indicators['sma_50'].iloc[latest_idx])),
            "sma_50": float(indicators['sma_50'].iloc[latest_idx]) if not as_string else str(float(indicators['sma_50'].iloc[latest_idx])),
            "ema_20": float(indicators['ema_20'].iloc[latest_idx]) if not as_string else str(float(indicators['ema_20'].iloc[latest_idx])),
            "rsi": float(indicators['rsi'].iloc[latest_idx]) if not as_string else str(float(indicators['rsi'].iloc[latest_idx])),
            "macd": {
                "line": float(indicators['macd'].iloc[latest_idx]) if not as_string else str(float(indicators['macd'].iloc[latest_idx])),
                "signal": float(indicators['macd_signal'].iloc[latest_idx]) if not as_string else str(float(indicators['macd_signal'].iloc[latest_idx])),
                "histogram": float(indicators['macd'].iloc[latest_idx] - indicators['macd_signal'].iloc[latest_idx]) if not as_string else str(float(indicators['macd'].iloc[latest_idx] - indicators['macd_signal'].iloc[latest_idx]))
            },
            "bollinger_bands": {
                "upper": float(indicators['bbands']['upper'].iloc[latest_idx]) if not as_string else str(float(indicators['bbands']['upper'].iloc[latest_idx])),
                "middle": float(indicators['bbands']['middle'].iloc[latest_idx]) if not as_string else str(float(indicators['bbands']['middle'].iloc[latest_idx])),
                "lower": float(indicators['bbands']['lower'].iloc[latest_idx]) if not as_string else str(float(indicators['bbands']['lower'].iloc[latest_idx]))
            },
            "mfi": 50.0  # You'll need to implement MFI calculation if needed
        }
        
        return result

    def _get_advanced_indicators(self, as_string: bool = False) -> Dict:
        """Get the latest advanced indicators"""
        indicators = self.advanced_calculator.indicators
        latest_idx = -1
        
        result = {
            "sma_20": float(indicators['sma_50'].iloc[latest_idx]) if not as_string else str(float(indicators['sma_50'].iloc[latest_idx])),
            "sma_50": float(indicators['sma_50'].iloc[latest_idx]) if not as_string else str(float(indicators['sma_50'].iloc[latest_idx])),
            "ema_20": float(indicators['ema_20'].iloc[latest_idx]) if not as_string else str(float(indicators['ema_20'].iloc[latest_idx])),
            "rsi": float(indicators['rsi'].iloc[latest_idx]) if not as_string else str(float(indicators['rsi'].iloc[latest_idx])),
            "macd": {
                "line": float(indicators['macd'].iloc[latest_idx]) if not as_string else str(float(indicators['macd'].iloc[latest_idx])),
                "signal": float(indicators['macd_signal'].iloc[latest_idx]) if not as_string else str(float(indicators['macd_signal'].iloc[latest_idx])),
                "histogram": float(indicators['macd'].iloc[latest_idx] - indicators['macd_signal'].iloc[latest_idx]) if not as_string else str(float(indicators['macd'].iloc[latest_idx] - indicators['macd_signal'].iloc[latest_idx]))
            },
            "bollinger_bands": {
                "upper": float(indicators['bbands']['upper'].iloc[latest_idx]) if not as_string else str(float(indicators['bbands']['upper'].iloc[latest_idx])),
                "middle": float(indicators['bbands']['middle'].iloc[latest_idx]) if not as_string else str(float(indicators['bbands']['middle'].iloc[latest_idx])),
                "lower": float(indicators['bbands']['lower'].iloc[latest_idx]) if not as_string else str(float(indicators['bbands']['lower'].iloc[latest_idx]))
            },
            "mfi": 50.0  # You'll need to implement MFI calculation if needed
        }
        
        return result 