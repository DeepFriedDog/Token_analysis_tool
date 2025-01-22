from abc import ABC, abstractmethod
import pandas as pd
from decimal import Decimal
from typing import Dict, Any

class BaseProcessor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def fetch_data(self, contract_address: str, timeframe: str, interval_days: int) -> pd.DataFrame:
        """Fetch price data for the given token"""
        pass

    def _validate_price_data(self, df: pd.DataFrame) -> bool:
        """Validate the price data DataFrame"""
        if df.empty:
            return False
        if not all(col in df.columns for col in ['timestamp', 'close']):
            return False
        if df['close'].isnull().any() or (df['close'] <= 0).any():
            return False
        return True

    def _process_price_data(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Process and resample price data"""
        if df.empty:
            return df
            
        if not isinstance(df.index, pd.DatetimeIndex):
            df.set_index('timestamp', inplace=True)
            
        rule_map = {'1m': '1Min', '5m': '5Min', '15m': '15Min', '1h': '1H', '4h': '4H', '1d': '1D'}
        rule = rule_map.get(timeframe, '1H')
        
        resampled = df.resample(rule).agg({
            'close': 'last',
            'high': 'max',
            'low': 'min',
            'open': 'first',
            'volume': 'sum'
        }).dropna()
        
        return resampled

    def _get_interval_seconds(self, timeframe: str) -> int:
        """Convert timeframe to seconds"""
        timeframe_map = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '1h': 3600,
            '4h': 14400,
            '1d': 86400
        }
        return timeframe_map.get(timeframe, 3600)