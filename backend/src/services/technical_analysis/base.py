from typing import List, Dict
import numpy as np
import pandas as pd
from decimal import Decimal
import talib

class BaseTechnicalAnalysis:
    def __init__(self, price_data: pd.DataFrame):
        """
        Initialize with price data DataFrame containing columns:
        timestamp, open, high, low, close, volume
        """
        self.df = price_data.copy()
        if not isinstance(self.df.index, pd.DatetimeIndex):
            if 'timestamp' in self.df.columns:
                self.df.set_index('timestamp', inplace=True)
            else:
                raise ValueError("DataFrame must have either a DatetimeIndex or a 'timestamp' column")

        # Convert price columns to numpy arrays for TA-Lib
        self.close_prices = self.df['close'].astype(float).values
        self.high_prices = self.df['high'].astype(float).values
        self.low_prices = self.df['low'].astype(float).values

    def prepare_data(self) -> None:
        """Prepare data for analysis"""
        self.df['returns'] = self.df['close'].pct_change()
        self.df['volatility'] = self.df['returns'].rolling(window=20).std() 

    def calculate_advanced_indicators(self) -> Dict:
        """Calculate advanced technical indicators"""
        # Trend Indicators
        sma_20 = talib.SMA(self.close_prices, timeperiod=20)
        sma_50 = talib.SMA(self.close_prices, timeperiod=50)
        ema_20 = talib.EMA(self.close_prices, timeperiod=20)
        
        # Momentum Indicators
        rsi = talib.RSI(self.close_prices, timeperiod=14)
        macd, macd_signal, macd_hist = talib.MACD(self.close_prices)
        
        # Volatility Indicators
        bbands_upper, bbands_middle, bbands_lower = talib.BBANDS(
            self.close_prices, 
            timeperiod=20,
            nbdevup=2,
            nbdevdn=2
        )
        
        # Volume Profile
        typical_price = (self.high_prices + self.low_prices + self.close_prices) / 3
        money_flow_index = talib.MFI(
            self.high_prices,
            self.low_prices,
            self.close_prices,
            self.df['volume'].astype(float).values,
            timeperiod=14
        )
        
        return {
            'sma_20': sma_20,
            'sma_50': sma_50,
            'ema_20': ema_20,
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'bbands': {
                'upper': bbands_upper,
                'middle': bbands_middle,
                'lower': bbands_lower
            },
            'mfi': money_flow_index
        }