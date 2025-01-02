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
                "fibonacci_levels": fibonacci,
                "advanced_indicators": {
                    "macd": macd,
                    "bollinger_bands": bollinger
                }
            }
        except Exception as e:
            print(f"[Analysis] ❌ Error during analysis: {str(e)}")
            raise

    def calculate_fibonacci_levels(self) -> List[Dict]:
        """Calculate Fibonacci retracement levels"""
        try:
            high = max(self.price_data['high'])
            low = min(self.price_data['low'])
            diff = high - low
            
            levels = [0.236, 0.382, 0.5, 0.618, 0.786]
            return [
                {
                    'level': level,
                    'price': float(high - (diff * Decimal(str(level)))),
                    'type': 'retracement'
                }
                for level in levels
            ]
        except Exception as e:
            print(f"[Analysis] Error calculating Fibonacci levels: {str(e)}")
            return [] 

    def calculate_macd(self) -> Dict:
        """Calculate MACD (12/26/9 periods)"""
        try:
            # Convert prices to Decimal
            prices = [Decimal(str(price)) for price in self.price_data['close']]
            
            # Calculate EMAs
            ema12 = self._calculate_ema(prices, 12)
            ema26 = self._calculate_ema(prices, 26)
            
            # Calculate MACD line
            macd_line = ema12 - ema26
            
            # Calculate signal line (9-day EMA of MACD line)
            signal_line = self._calculate_ema([macd_line], 9)
            
            # Calculate histogram
            histogram = macd_line - signal_line
            
            return {
                'line': float(macd_line),
                'signal': float(signal_line),
                'histogram': float(histogram)
            }
        except Exception as e:
            print(f"[Analysis] ⚠️ Error calculating MACD: {str(e)}")
            return {'line': 0, 'signal': 0, 'histogram': 0}

    def _calculate_ema(self, prices: List[Decimal], period: int) -> Decimal:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return Decimal('0')
        
        multiplier = Decimal('2') / (Decimal(str(period)) + Decimal('1'))
        ema = sum(prices[:period]) / Decimal(str(period))
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (Decimal('1') - multiplier))
        
        return ema 