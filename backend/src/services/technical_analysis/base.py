from typing import List, Dict
import numpy as np
import pandas as pd
from decimal import Decimal

class BaseTechnicalAnalysis:
    def __init__(self, df: pd.DataFrame):
        """
        Initialize with price data DataFrame containing columns:
        timestamp, open, high, low, close, volume
        """
        self.df = df
        if not isinstance(self.df.index, pd.DatetimeIndex):
            if 'timestamp' in self.df.columns:
                self.df.set_index('timestamp', inplace=True)
            else:
                raise ValueError("DataFrame must have either a DatetimeIndex or a 'timestamp' column")

        # Convert price columns to numpy arrays for TA-Lib
        self.close_prices = self.df['close'].astype(float).values
        self.high_prices = self.df['high'].astype(float).values if 'high' in self.df else self.close_prices
        self.low_prices = self.df['low'].astype(float).values if 'low' in self.df else self.close_prices

    def prepare_data(self) -> None:
        """Prepare data for analysis"""
        self.df['returns'] = self.df['close'].pct_change()
        self.df['volatility'] = self.df['returns'].rolling(window=20).std() 

    def calculate_advanced_indicators(self) -> Dict:
        """Calculate advanced technical indicators using pandas implementations"""
        df = pd.DataFrame({'close': self.close_prices})
        
        # Calculate indicators using the same methods as AdvancedDCACalculator
        # Reference: backend/src/services/dca/advanced_calculator.py lines 89-128
        close_prices = pd.Series(self.close_prices)
        
        # RSI calculation
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Moving Averages
        sma_20 = close_prices.rolling(window=20).mean()
        sma_50 = close_prices.rolling(window=50).mean()
        ema_20 = close_prices.ewm(span=20, adjust=False).mean()
        
        # MACD
        exp1 = close_prices.ewm(span=12, adjust=False).mean()
        exp2 = close_prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        bb_middle = close_prices.rolling(window=20).mean()
        rolling_std = close_prices.rolling(window=20).std()
        bb_upper = bb_middle + (rolling_std * 2)
        bb_lower = bb_middle - (rolling_std * 2)
        
        return {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'ema_20': ema_20,
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'bbands': {
                'upper': bb_upper,
                'middle': bb_middle,
                'lower': bb_lower
            }
        }