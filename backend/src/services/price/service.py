from typing import Dict, List, Optional
from datetime import datetime, timedelta
import aiohttp
import pandas as pd
from .exceptions import PriceDataError
from .processors.defillama import DefiLlamaProcessor
from ..technical_analysis.analyzer import TechnicalAnalyzer
from decimal import Decimal, ROUND_DOWN, InvalidOperation
from .processors.ludo import LudoProcessor

class PriceService:
    def __init__(self):
        self.ludo_processor = LudoProcessor()
        self.defillama_processor = DefiLlamaProcessor()
        pd.set_option('display.float_format', lambda x: f'{x:.8f}')
        pd.set_option('display.precision', 8)

    async def get_price_data(self, contract_address: str, timeframe: str, interval_days: int) -> Dict:
        """Fetch and process price data with preserved precision"""
        try:
            print(f"[Price] 🔍 Analyzing {contract_address}")
            print(f"[Price] ⚙️ Parameters: {timeframe} intervals, {interval_days} days")
            
            # First try fetching price data using Ludo
            df = await self.ludo_processor.fetch_data(contract_address, timeframe, interval_days)
            if not df.empty:
                print(f"[Ludo] ✅ Found {len(df)} price points")
            else:
                print(f"[Price] ⚠️ Ludo returned no data. Falling back to DefiLlama.")
                df = await self.defillama_processor.fetch_data(contract_address, timeframe, interval_days)
                if df.empty:
                    raise PriceDataError("No price data found", "defillama")
                print(f"[DefiLlama] ✅ Found {len(df)} price points with 8 decimals")
            
            # Validate that the returned price data meets a minimum threshold.
            # Define expected price points per day for each timeframe.
            points_per_day = {"15m": 96, "1h": 24, "4h": 6, "1d": 1}
            # Define a minimal required count for a reliable DCA calculation.
            min_required = {"15m": 100, "1h": 50, "4h": 30, "1d": 15}
            if timeframe in points_per_day:
                if len(df) < min_required[timeframe]:
                    suggested_days = -(-min_required[timeframe] // points_per_day[timeframe])
                    print(f"[Price] ⚠️ Insufficient price data: found {len(df)} price points, but at least {min_required[timeframe]} are recommended for timeframe {timeframe}.")
                    print(f"[Price] Consider increasing interval_days to at least {suggested_days} days for a robust DCA calculation.")
            
            # Convert price columns to Decimal with 8 decimal precision
            for col in ['close', 'high', 'low']:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: Decimal(str(x)).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN))
            
            print("[Price] ✅ Successfully fetched price points")
            
            # Format price data for frontend chart
            price_history = []
            for timestamp, row in df.iterrows():
                # Convert timestamp to milliseconds for frontend chart
                ts_ms = int(pd.Timestamp(timestamp).timestamp() * 1000)
                price_point = {
                    'timestamp': ts_ms,  # Frontend expects milliseconds timestamp
                    'value': str(row['close']),  # Frontend expects string for precision
                    'formatted': {
                        'price': str(row['close']),  # Keep string version for precision
                        'high': str(row.get('high', row['close'])),
                        'low': str(row.get('low', row['close']))
                    }
                }
                price_history.append(price_point)
            
            # Sort by timestamp to ensure proper chart rendering
            price_history.sort(key=lambda x: x['timestamp'])
            
            # Calculate technical indicators
            technical_analysis = self.calculate_technical_indicators(df)
            
            return {
                'priceData': {
                    'price_history': price_history,
                    'current_price': str(df['close'].iloc[-1]) if not df.empty else "0"
                },
                'technical_analysis': technical_analysis
            }
            
        except Exception as e:
            print(f"[Price] ❌ Error: {str(e)}")
            raise PriceDataError(f"Error fetching price data: {str(e)}", "price_service")

    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate technical indicators using TechnicalAnalyzer"""
        try:
            print("[Analysis] 📊 Calculating technical indicators...")
            analyzer = TechnicalAnalyzer(df)
            result = analyzer.analyze()
            print("[Analysis] ✅ Technical analysis complete")
            return result
            
        except InvalidOperation as e:
            print(f"[Analysis] ❌ Decimal conversion error: {str(e)}")
            return {
                'support_levels': [],
                'resistance_levels': [],
                'rsi': str(Decimal('50.0')),
                'volatility': str(Decimal('0.0')),
                'fibonacci_levels': [],
                'advanced_indicators': {
                    'macd': {'line': '0', 'signal': '0', 'histogram': '0'},
                    'bollinger_bands': {'upper': '0', 'middle': '0', 'lower': '0'}
                }
            }
        except Exception as e:
            print(f"[Analysis] ❌ Error calculating indicators: {str(e)}")
            raise PriceDataError(
                message=f"Error calculating technical indicators: {str(e)}",
                source="analysis",
                status_code=500
            )