import aiohttp
import pandas as pd
from decimal import Decimal
from datetime import datetime
from .base import BaseProcessor
import asyncio
import decimal

class DefiLlamaProcessor(BaseProcessor):
    def __init__(self):
        self.base_url = "https://coins.llama.fi"
        
    async def fetch_data(self, contract_address: str, timeframe: str, interval_days: int) -> pd.DataFrame:
        try:
            token_id = f"ethereum:{contract_address.lower()}"
            end_time = int(datetime.now().timestamp())
            start_time = end_time - (interval_days * 24 * 60 * 60)
            interval = self._get_interval_seconds(timeframe)
            
            price_data = []
            async with aiohttp.ClientSession() as session:
                current_time = start_time
                while current_time <= end_time:
                    url = f"{self.base_url}/prices/historical/{current_time}/{token_id}"
                    
                    async with session.get(url) as response:
                        if response.status == 429:  # Rate limit hit
                            print(f"[DefiLlama] ⚠️ Rate limit reached. Please try again later.")
                            return pd.DataFrame()
                        elif response.status == 200:
                            data = await response.json()
                            if data and 'coins' in data and token_id in data['coins']:
                                try:
                                    price_info = data['coins'][token_id]
                                    price = Decimal(str(price_info['price']))
                                    if price > 0:  # Ensure price is positive
                                        price_data.append({
                                            'timestamp': datetime.fromtimestamp(current_time),
                                            'close': price,
                                            'open': price,
                                            'high': price,
                                            'low': price,
                                            'volume': Decimal('0')
                                        })
                                except (ValueError, TypeError, decimal.InvalidOperation) as e:
                                    print(f"[DefiLlama] ⚠️ Error converting price: {str(e)}")
                                    continue
                
                    current_time += interval
                    await asyncio.sleep(0.2)  # Rate limiting

            if not price_data:
                return pd.DataFrame()
                
            # Create DataFrame with high precision
            df = pd.DataFrame(price_data)
            df.set_index('timestamp', inplace=True)
            
            # Ensure price columns maintain precision by storing as strings
            for col in ['open', 'high', 'low', 'close']:
                df[col] = df[col].astype('object')  # Store as strings for Decimal conversion
            
            df.sort_index(inplace=True)
            print(f"[DefiLlama] ✅ Found {len(df)} price points with {len(str(df['close'].iloc[0]).split('.')[-1])} decimals")
            
            return df
                    
        except Exception as e:
            print(f"[DefiLlama] ❌ Error: {str(e)}")
            return pd.DataFrame()
            
    def _get_interval_seconds(self, timeframe: str) -> int:
        """Convert timeframe to seconds"""
        interval_map = {
            '15m': 15 * 60,
            '1h': 60 * 60,
            '4h': 4 * 60 * 60,
            '1d': 24 * 60 * 60
        }
        return interval_map.get(timeframe, 60 * 60)  # default to 1h
        