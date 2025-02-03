from .support_resistance import SupportResistanceAnalyzer
from .fibonacci import FibonacciAnalyzer
from .base import BaseTechnicalAnalysis
import pandas as pd
import numpy as np
from typing import Dict, List
from decimal import Decimal
import logging

class TechnicalAnalyzer:
    def __init__(self, price_data: pd.DataFrame):
        self.price_data = price_data
        # Convert price data to Decimal
        for col in ['open', 'high', 'low', 'close']:
            if col in self.price_data:
                self.price_data[col] = self.price_data[col].apply(lambda x: Decimal(str(x)))
        
        self.sr_analyzer = SupportResistanceAnalyzer(price_data)
        self.fib_analyzer = FibonacciAnalyzer(price_data)

    def calculate_rsi(self, period: int = 14) -> float:
        """Calculate RSI for the latest period"""
        try:
            delta = self.price_data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50.0
        except Exception:
            return 50.0

    def calculate_volatility(self, period: int = 20) -> float:
        """Calculate volatility (standard deviation of returns)"""
        try:
            # Convert prices to Decimal and calculate returns
            close_prices = [Decimal(str(price)) for price in self.price_data['close']]
            returns = []
            
            for i in range(1, len(close_prices)):
                if close_prices[i-1] > Decimal('0'):
                    ret = (close_prices[i] - close_prices[i-1]) / close_prices[i-1]
                    returns.append(float(ret))  # Convert to float for numpy operations
                else:
                    returns.append(0.0)
            
            # Calculate standard deviation using numpy and convert back to Decimal
            std_dev = Decimal(str(np.std(returns)))
            sqrt_period = Decimal(str(np.sqrt(period)))
            vol = std_dev * sqrt_period * Decimal('100')  # Convert to percentage
            
            return float(vol) if not pd.isna(vol) else 0.0
            
        except Exception as e:
            print(f"[Analysis] ⚠️ Error calculating volatility: {str(e)}")
            return 0.0

    def calculate_bollinger_bands(self) -> Dict:
        """Calculate Bollinger Bands (20-period SMA with 2 standard deviations)"""
        try:
            # Convert prices to Decimal
            prices = [Decimal(str(price)) for price in self.price_data['close']]
            
            # Calculate 20-period SMA
            period = 20
            if len(prices) < period:
                return {'upper': 0, 'middle': 0, 'lower': 0}
            
            sma = sum(prices[-period:]) / Decimal(str(period))
            
            # Calculate standard deviation
            squared_diff = sum((price - sma) ** 2 for price in prices[-period:])
            std_dev = (squared_diff / Decimal(str(period))).sqrt()
            
            # Calculate bands
            upper_band = sma + (Decimal('2') * std_dev)
            lower_band = sma - (Decimal('2') * std_dev)
            
            return {
                'upper': float(upper_band),
                'middle': float(sma),
                'lower': float(lower_band)
            }
        except Exception as e:
            print(f"[Analysis] ⚠️ Error calculating Bollinger Bands: {str(e)}")
            return {'upper': 0, 'middle': 0, 'lower': 0}

    def analyze(self) -> Dict:
        """Perform complete technical analysis"""
        try:
            print("[Analysis] 📊 Starting technical analysis...")
            
            support_levels, resistance_levels = self.sr_analyzer.find_levels()
            trend = 'up' if self.price_data['close'].iloc[-1] > self.price_data['close'].iloc[0] else 'down'
            
            # Convert numeric values
            support_levels = [Decimal(str(level)) for level in support_levels if not pd.isna(level)]
            resistance_levels = [Decimal(str(level)) for level in resistance_levels if not pd.isna(level)]
            
            # Calculate indicators
            rsi = self.calculate_rsi()
            volatility = self.calculate_volatility()
            macd = self.calculate_macd()
            bollinger = self.calculate_bollinger_bands()
            fibonacci = self.calculate_fibonacci_levels()
            
            print("[Analysis] ✅ Technical analysis complete")
            
            return {
                "support_levels": support_levels,
                "resistance_levels": resistance_levels,
                "trend": trend,
                "rsi": str(rsi),
                "volatility": str(volatility),
                "advanced_indicators": {
                    "macd": macd,
                    "bollinger_bands": bollinger,
                    "fibonacci_levels": fibonacci
                }
            }
        except Exception as e:
            print(f"[Analysis] ❌ Error during analysis: {str(e)}")
            raise

    def calculate_fibonacci_levels(self) -> List[Dict]:
        """Calculate Fibonacci retracement levels using FibonacciAnalyzer"""
        try:
            fib_analyzer = FibonacciAnalyzer(self.price_data)
            current_price = float(self.price_data['close'].iloc[-1])
            trend = 'up' if current_price > float(self.price_data['close'].iloc[0]) else 'down'
            
            levels = fib_analyzer.calculate_levels(trend)
            
            # Sort levels by price for better organization
            sorted_levels = sorted(levels, key=lambda x: x['price'], reverse=True)
            
            # Transform and enrich the output
            return [
                {
                    'level': level['level'],
                    'price': float(level['price']),
                    'label': level['type'],
                    'strength': self._calculate_level_strength(float(level['price']), current_price),
                    'recommendation': self._get_level_recommendation(
                        float(level['price']), 
                        current_price, 
                        level['level']
                    )
                }
                for level in sorted_levels
            ]
        except Exception as e:
            print(f"[Analysis] Error calculating Fibonacci levels: {str(e)}")
            return []

    def _calculate_level_strength(self, level_price: float, current_price: float) -> float:
        """Calculate how strong a Fibonacci level is based on historical price action"""
        try:
            price_data = self.price_data['close'].astype(float)
            threshold = 0.01  # 1% range around level
            touches = sum(1 for price in price_data if abs(price - level_price) / level_price <= threshold)
            max_touches = len(price_data) * 0.1  # Normalize against 10% of total periods
            return min(touches / max_touches, 1.0)
        except Exception:
            return 0.0

    def _get_level_recommendation(self, level_price: float, current_price: float, fib_ratio: float) -> str:
        """Generate trading recommendations based on Fibonacci level analysis"""
        price_diff = ((level_price - current_price) / current_price) * 100
        
        if level_price < current_price:
            if fib_ratio <= 0.382:
                return "Strong support - Consider for major position entry"
            elif fib_ratio <= 0.618:
                return "Moderate support - Good for DCA entry"
            else:
                return "Weak support - Small position entry"
        else:
            if abs(price_diff) < 5:
                return "Near resistance - Consider taking partial profits"
            elif fib_ratio >= 1.618:
                return "Major resistance - Consider exit"
            else:
                return "Resistance zone - Reduce position size"

    def calculate_macd(self) -> Dict:
        """Calculate MACD (12/26/9 periods) using pandas for improved precision"""
        try:
            # Convert 'close' prices to float values
            prices = self.price_data['close'].astype(float)
            # Calculate the 12-period and 26-period EMAs
            ema12 = prices.ewm(span=12, adjust=False).mean()
            ema26 = prices.ewm(span=26, adjust=False).mean()
            # Compute the MACD line and then the 9-period EMA on the MACD line (signal)
            macd_series = ema12 - ema26
            signal_series = macd_series.ewm(span=9, adjust=False).mean()
            histogram_series = macd_series - signal_series

            # Retrieve the latest values and round to 4 decimal places
            macd_line = macd_series.iloc[-1]
            signal_line = signal_series.iloc[-1]
            histogram = histogram_series.iloc[-1]

            return {
                'line': float(round(macd_line, 4)),
                'signal': float(round(signal_line, 4)),
                'histogram': float(round(histogram, 4))
            }
        except Exception as e:
            print(f"[Analysis] ⚠️ Error calculating MACD: {str(e)}")
            return {'line': 0, 'signal': 0, 'histogram': 0}

    def get_advanced_indicators(self) -> dict:
        """
        Gather advanced indicators including MACD and Fibonacci levels.
        """
        return {
            "macd": self.calculate_macd(),
            "fibonacci_levels": self.calculate_fibonacci_levels()
        }

"""Technical analysis module using pandas-based implementations.

This module provides technical analysis functionality using native pandas operations
rather than external libraries. It includes implementations for:
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Support/Resistance levels
- Fibonacci retracements
""" 