import aiohttp
import pandas as pd
from datetime import datetime
from .base import BaseProcessor
from ..exceptions import PriceDataError
import asyncio

class LudoProcessor(BaseProcessor):
    def __init__(self):
        self.base_url = "http://148.251.91.241:3535"

    async def fetch_data(self, contract_address: str, timeframe: str, interval_days: int) -> pd.DataFrame:
        """Fetch historical price data from Ludo API with fallback to DefiLlama if necessary"""
        try:
            from datetime import timedelta
            base_api = "http://148.251.91.241:3535"
            volumes_url = f"{base_api}/volumes"
            contract_lower = contract_address.lower()

            async with aiohttp.ClientSession() as session:
                # Check if the contract is monitored by Ludo
                async with session.get(volumes_url) as vol_resp:
                    if vol_resp.status != 200:
                        print(f"[Ludo] ⚠️ Error fetching volumes from {volumes_url}: Status {vol_resp.status}")
                        from .defillama import DefiLlamaProcessor
                        fallback = DefiLlamaProcessor()
                        return await fallback.fetch_data(contract_address, timeframe, interval_days)
                    volumes_data = await vol_resp.json()

                monitored = False
                if isinstance(volumes_data, dict):
                    # Compare against lower-cased keys to account for case differences
                    monitored = contract_lower in [key.lower() for key in volumes_data.keys()]
                elif isinstance(volumes_data, list):
                    for vol in volumes_data:
                        if isinstance(vol, dict) and vol.get("contract", "").lower() == contract_lower:
                            monitored = True
                            break
                        elif isinstance(vol, str) and vol.lower() == contract_lower:
                            monitored = True
                            break
                else:
                    monitored = False
                print(f"[Ludo] DEBUG: Token {contract_lower} {'is' if monitored else 'is NOT'} in Ludo Volume list. Available keys: {list(volumes_data.keys()) if isinstance(volumes_data, dict) else 'Not a dict'}")

                print(f"[Ludo] DEBUG: Monitored flag for token {contract_lower} is {monitored}.")
                if monitored:
                    print(f"[Ludo] ✅ Token {contract_lower} found in volumes data from {volumes_url}. Starting Ludo data extraction.")
                else:
                    print(f"[Ludo] ⚠️ Token {contract_lower} NOT found in volumes data from {volumes_url}. Falling back to DefiLlama.")
                    from .defillama import DefiLlamaProcessor
                    fallback = DefiLlamaProcessor()
                    return await fallback.fetch_data(contract_address, timeframe, interval_days)

                # Fetch historical price data via volume endpoints
                page = 0
                price_points = []
                cutoff_time = datetime.now() - timedelta(days=interval_days)
                total_pages = 0
                print(f"[Ludo] Starting to fetch price data for token {contract_lower}. Analysis period cutoff is {cutoff_time}.")
                while True:
                    volume_url = f"{base_api}/volume/{contract_lower}/{page}"
                    print(f"[Ludo] 🌐 Fetching price data from {volume_url}")
                    async with session.get(volume_url) as vol_resp:
                        if vol_resp.status != 200:
                            print(f"[Ludo] ⚠️ Error fetching volume data from {volume_url}: Status {vol_resp.status}")
                            break
                        volume_data = await vol_resp.json()
                        if not volume_data:
                            print(f"[Ludo] ⚠️ No more volume data returned from page {page}.")
                            break

                        record_count = len(volume_data)
                        print(f"[Ludo] ✅ Successfully fetched {record_count} records from page {page}.")

                        stop_fetch = False
                        # Process timestamps in descending order to correctly apply the cutoff.
                        for ts_str in sorted(volume_data.keys(), key=lambda ts: int(ts), reverse=True):
                            try:
                                ts_int = int(ts_str)
                            except ValueError:
                                print(f"[Ludo] ⚠️ Could not convert timestamp {ts_str} to int, skipping...")
                                continue
                            dt = datetime.fromtimestamp(ts_int)
                            if dt < cutoff_time:
                                print(f"[Ludo] ⚠️ Record timestamp {dt} is before cutoff time {cutoff_time}. Stopping page processing.")
                                stop_fetch = True
                                break
                            data_point = volume_data[ts_str]
                            price_points.append({
                                "timestamp": dt,
                                "price": data_point.get("price", 0),
                                "close": data_point.get("price", 0),
                                "low": data_point.get("price", 0),
                                "volume": data_point.get("volume", 0)
                            })
                        if stop_fetch:
                            print(f"[Ludo] Reached data before analysis period on page {page}; stopping further requests.")
                            break
                        page += 1
                        total_pages += 1
                        await asyncio.sleep(0.2)
                print(f"[Ludo] ✅ Completed fetching data from Ludo. Total pages processed: {total_pages}, total records collected: {len(price_points)}.")

                if not price_points:
                    print("[Ludo] ⚠️ No price points found from Ludo API. Falling back to DefiLlama.")
                    from .defillama import DefiLlamaProcessor
                    fallback = DefiLlamaProcessor()
                    return await fallback.fetch_data(contract_address, timeframe, interval_days)

                df = pd.DataFrame(price_points)
                df.set_index("timestamp", inplace=True)
                df.sort_index(inplace=True)
                df = self._resample_timeframe(df, timeframe)
                print(f"[Ludo] ✅ Found {len(df)} price points")
                return df

        except asyncio.CancelledError:
            raise
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
            'close': 'last',
            'low': 'min'
        })
        # Set default values for missing columns for consistency with DefiLlama output
        resampled['open'] = resampled['close']
        resampled['high'] = resampled['close']
        if 'volume' not in resampled.columns:
            resampled['volume'] = 0
        
        return resampled 