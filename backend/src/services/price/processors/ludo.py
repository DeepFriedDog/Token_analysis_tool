import aiohttp
import pandas as pd
from datetime import datetime
from .base import BaseProcessor
from ..exceptions import PriceDataError
import asyncio

class LudoProcessor(BaseProcessor):
    def __init__(self):
        self.base_url = "http://storage.ludo.com:3535/volume"

    async def fetch_data(self, contract_address: str, timeframe: str, interval_days: int) -> pd.DataFrame:
        """Fetch historical price data from Ludo storage"""
        try:
            url = f"{self.base_url}/{contract_address.lower()}"
            
            print(f"\n[Ludo] 🌐 Fetching price data")
            print(f"[Ludo] 📊 Timeframe: {timeframe}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        print(f"[Ludo] ⚠️ Error: Status {response.status}")
                        return pd.DataFrame()
                        
                    data = await response.json()
                    if not data:
                        print("[Ludo] ⚠️ No data returned")
                        return pd.DataFrame()
                    
                    # Convert data to DataFrame
                    df = pd.DataFrame(data)
                    if df.empty:
                        return df
                    
                    # Process timestamps and prices
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                    df.set_index('timestamp', inplace=True)
                    df.sort_index(inplace=True)
                    
                    # Resample to desired timeframe
                    df = self._resample_timeframe(df, timeframe)
                    
                    print(f"[Ludo] ✅ Found {len(df)} price points")
                    return df
                    
        except Exception as e:
            print(f"[Ludo] ❌ Error: {str(e)}")
            return pd.DataFrame()

    def _resample_timeframe(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Resample data to desired timeframe"""
        interval_map = {
            '15m': '15T',
            '1h': 'H',
            '4h': '4H',
            '1d': 'D'
        }
        rule = interval_map.get(timeframe, 'H')
        
        resampled = df.resample(rule).agg({
            'price': 'last',
            'volume': 'sum'
        }).dropna()
        
        return resampled 