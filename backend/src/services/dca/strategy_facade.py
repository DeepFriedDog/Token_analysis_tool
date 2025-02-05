from decimal import Decimal, ROUND_HALF_UP
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
        try:
            price_data = [
                {
                    'timestamp': str(timestamp),
                    'close': str(row['close']),
                    'high': str(row.get('high', row['close'])),
                    'low': str(row.get('low', row['close']))
                }
                for timestamp, row in self.price_data.iterrows()
            ]
            
            # Compute DCA and exit strategies
            dca_strategy = self.get_dca_and_exit_strategy(support_levels, resistance_levels, fibonacci_levels)
            
            # Get advanced indicators
            advanced_indicators = self._get_advanced_indicators(as_string=True)
            
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
                    "advanced_indicators": advanced_indicators,
                    "dca_strategy": dca_strategy,
                    "dca_recommendations": {
                        "entry_zones": self._transform_entry_strategy(dca_strategy["entry_strategy"]),
                        "risk_assessment": {
                            "overall_risk": 0.5,
                            "key_risks": []
                        }
                    }
                }
            }
        except Exception as e:
            print(f"[Analysis] ⚠️ Error in get_analysis_result: {str(e)}")
            return self._get_empty_result()

    def calculate_dca_strategy(self, support_levels: List[float]) -> List[Dict]:
        current_price = Decimal(str(self.price_data['close'].iloc[-1]))
        valid_entries = [Decimal(str(level)) for level in support_levels if Decimal(str(level)) < current_price]
        if not valid_entries:
            return []
        total_diff = sum([current_price - level for level in valid_entries])
        strategy = []
        for level in valid_entries:
            weight = (current_price - level) / total_diff if total_diff != 0 else Decimal('0')
            allocation = (self.investment_amount * weight).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            strategy.append({
                "entry_price": float(level),
                "allocation": float(allocation)
            })
        return strategy

    def calculate_exit_strategy(self, resistance_levels: List[float], fibonacci_levels: List[Dict]) -> Dict:
        current_price = Decimal(str(self.price_data['close'].iloc[-1]))
        valid_resistances = [Decimal(str(level)) for level in resistance_levels if Decimal(str(level)) > current_price]
        for fib in fibonacci_levels:
            fib_price = Decimal(str(fib['price']))
            if fib_price > current_price and Decimal(str(fib.get('level', 0))) > Decimal('1'):
                valid_resistances.append(fib_price)
        if not valid_resistances:
            return {"sell_percentage": 0, "exit_price": float(current_price)}
        best_exit = min(valid_resistances)
        gap_percentage = (best_exit - current_price) / current_price * Decimal('100')
        if gap_percentage < Decimal('5'):
            sell_percentage = 25
        elif gap_percentage < Decimal('10'):
            sell_percentage = 50
        elif gap_percentage < Decimal('15'):
            sell_percentage = 75
        else:
            sell_percentage = 100
        return {"sell_percentage": sell_percentage, "exit_price": float(best_exit)}

    def get_dca_and_exit_strategy(self, support_levels: List[float], resistance_levels: List[float], fibonacci_levels: List[Dict]) -> Dict:
        try:
            current_price = Decimal(str(self.price_data['close'].iloc[-1]))
            
            # Calculate entry strategy using all provided support levels regardless of current price.
            support_entries = [Decimal(str(level)) for level in support_levels]
            entry_strategy = []
            if support_entries:
                total_weight = sum([abs(current_price - level) for level in support_entries])
                if total_weight == 0:
                    total_weight = Decimal('1')
                for level in support_entries:
                    weight = abs(current_price - level) / total_weight
                    allocation = (self.investment_amount * weight).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    entry_strategy.append({
                        "entry_price": float(level),
                        "allocation": float(allocation)
                    })
            else:
                print("[DCA Strategy] ⚠️ No support levels provided; using current price as default entry.")
                entry_strategy = [{"entry_price": float(current_price), "allocation": 100.0}]
            
            # Calculate exit strategy using resistance levels and Fibonacci retracement input.
            valid_resistances = [Decimal(str(level)) for level in resistance_levels if Decimal(str(level)) > current_price]
            for fib in fibonacci_levels:
                fib_price = Decimal(str(fib['price']))
                if fib_price > current_price and Decimal(str(fib.get('level', 0))) > Decimal('1'):
                    valid_resistances.append(fib_price)
            
            exit_strategy = {
                "sell_percentage": 0,
                "exit_price": float(current_price)
            }
            
            if valid_resistances:
                best_exit = min(valid_resistances)
                gap_percentage = (best_exit - current_price) / current_price * Decimal('100')
                sell_percentage = 0
                if gap_percentage < Decimal('5'):
                    sell_percentage = 25
                elif gap_percentage < Decimal('10'):
                    sell_percentage = 50
                elif gap_percentage < Decimal('15'):
                    sell_percentage = 75
                else:
                    sell_percentage = 100
                exit_strategy = {
                    "sell_percentage": sell_percentage,
                    "exit_price": float(best_exit)
                }
            
            # Compute a confidence risk meter based on price volatility.
            try:
                volatility = self.basic_calculator.calculate_volatility()
                if volatility < Decimal('0.05'):
                    risk_confidence = 0.9
                elif volatility < Decimal('0.10'):
                    risk_confidence = 0.7
                else:
                    risk_confidence = 0.5
            except Exception as e:
                print(f"[DCA Strategy] ⚠️ Could not compute volatility: {str(e)}; defaulting risk confidence to 0.5")
                risk_confidence = 0.5

            return {
                "entry_strategy": entry_strategy,
                "exit_strategy": exit_strategy,
                "risk_confidence": risk_confidence
            }
        except Exception as e:
            print(f"[Strategy] ⚠️ Error in get_dca_and_exit_strategy: {str(e)}")
            return {
                "entry_strategy": [],
                "exit_strategy": {
                    "sell_percentage": 0,
                    "exit_price": 0
                }
            }

    def _get_advanced_indicators(self, as_string: bool = False) -> Dict:
        """Get the latest advanced indicators"""
        indicators = self.advanced_calculator.indicators
        if as_string:
            return {key: str(value) for key, value in indicators.items()}
        return indicators

    def _transform_entry_strategy(self, entry_strategy: List[Dict]) -> List[Dict]:
        return [
            {
                "price_level": entry["entry_price"],
                "allocation": entry["allocation"],
                "confidence": 0.8,  # Default confidence level
                "reasoning": ["Based on support level analysis"]
            }
            for entry in entry_strategy
        ]

    def _get_empty_result(self) -> Dict:
        return {
            "priceData": [],
            "technical_analysis": {
                "support_levels": [],
                "resistance_levels": [],
                "fibonacci_levels": [],
                "rsi": "N/A",
                "volatility": "N/A",
                "advanced_indicators": {},
                "dca_strategy": {
                    "entry_strategy": [],
                    "exit_strategy": {
                        "sell_percentage": 0,
                        "exit_price": 0
                    }
                },
                "dca_recommendations": {
                    "entry_zones": [],
                    "risk_assessment": {
                        "overall_risk": 0.5,
                        "key_risks": []
                    }
                }
            }
        } 