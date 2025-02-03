from .base import BaseTechnicalAnalysis
from typing import List, Dict
import pandas as pd
from decimal import Decimal

class FibonacciAnalyzer(BaseTechnicalAnalysis):
    def __init__(self, price_data: pd.DataFrame):
        super().__init__(price_data)
        self.fib_ratios = {
            'Extension 1.618': 1.618,
            'Extension 1.272': 1.272,
            'Peak': 1.0,
            'Retracement 0.786': 0.786,
            'Retracement 0.618': 0.618,
            'Retracement 0.5': 0.5,
            'Retracement 0.382': 0.382,
            'Retracement 0.236': 0.236,
            'Bottom': 0.0
        }

    def calculate_levels(self, trend: str = 'up') -> List[Dict]:
        """Calculate Fibonacci levels based on trend direction"""
        if trend == 'up':
            swing_low = self.df['close'].min()
            swing_high = self.df['close'].max()
        else:
            swing_low = self.df['close'].max()
            swing_high = self.df['close'].min()

        price_range = swing_high - swing_low
        levels = []

        for name, ratio in self.fib_ratios.items():
            # Convert the ratio from float to Decimal for consistent arithmetic
            ratio_dec = Decimal(str(ratio))
            if trend == 'up':
                price = swing_low + (price_range * ratio_dec)
            else:
                price = swing_high - (price_range * ratio_dec)

            levels.append({
                'level': ratio_dec,
                'price': price,
                'type': name
            })

        return levels 