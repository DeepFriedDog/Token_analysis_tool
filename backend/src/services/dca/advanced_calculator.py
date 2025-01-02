from typing import List, Dict
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
import talib
import numpy as np

class AdvancedDCACalculator:
    def __init__(self, price_data: pd.DataFrame, investment_amount: Decimal, risk_tolerance: Decimal = Decimal('0.5')):
        self.price_data = price_data
        self.total_investment = investment_amount
        self.risk_tolerance = risk_tolerance
        self.indicators = self._calculate_indicators()
    
    def _calculate_position_size(self, signal_strength: Decimal) -> Decimal:
        """Calculate position size based on signal strength and risk tolerance"""
        base_position = self.total_investment / Decimal('10')  # Base 10% of total investment
        signal_multiplier = Decimal('1') + (signal_strength * self.risk_tolerance)
        return base_position * signal_multiplier
    
    def _calculate_signal_strength(self, index: int) -> Decimal:
        """Calculate signal strength based on technical indicators"""
        signals = []
        
        # RSI Signal (Oversold conditions)
        rsi = Decimal(str(self.indicators['rsi'].iloc[index]))
        if rsi < Decimal('30'):
            signals.append(Decimal('0.8'))
        elif rsi < Decimal('40'):
            signals.append(Decimal('0.5'))
            
        # MACD Signal
        macd = Decimal(str(self.indicators['macd'].iloc[index]))
        macd_signal = Decimal(str(self.indicators['macd_signal'].iloc[index]))
        macd_prev = Decimal(str(self.indicators['macd'].iloc[index-1]))
        macd_signal_prev = Decimal(str(self.indicators['macd_signal'].iloc[index-1]))
        
        if macd > macd_signal and macd_prev <= macd_signal_prev:
            signals.append(Decimal('0.7'))
            
        # Bollinger Bands Signal
        price = Decimal(str(self.price_data['close'].iloc[index]))
        bb_lower = Decimal(str(self.indicators['bbands']['lower'].iloc[index]))
        if price < bb_lower:
            signals.append(Decimal('0.9'))
            
        # Moving Average Signal
        ema_20 = Decimal(str(self.indicators['ema_20'].iloc[index]))
        sma_50 = Decimal(str(self.indicators['sma_50'].iloc[index]))
        ema_20_prev = Decimal(str(self.indicators['ema_20'].iloc[index-1]))
        sma_50_prev = Decimal(str(self.indicators['sma_50'].iloc[index-1]))
        
        # Moving Average Crossover
        if ema_20 > sma_50 and ema_20_prev <= sma_50_prev:
            signals.append(Decimal('0.6'))
        
        if signals:
            return sum(signals) / Decimal(str(len(signals)))
        return Decimal('0')
    
    def calculate_entry_signals(self) -> List[Dict]:
        """Generate entry signals based on multiple indicators"""
        entry_signals = []
        
        for i in range(len(self.price_data)):
            if i < 50:  # Need enough data for indicators
                continue
                
            current_price = self._format_price(self.price_data['close'].iloc[i])
            
            # Calculate signal strength based on multiple factors
            signal_strength = self._calculate_signal_strength(i)
            
            if signal_strength > Decimal('0.7'):  # Strong buy signal
                position_size = self._calculate_position_size(signal_strength)
                entry_signals.append({
                    'price': current_price,
                    'timestamp': self.price_data.index[i].isoformat(),
                    'signal_strength': float(signal_strength),
                    'position_size': float(position_size),
                    'indicators': self._get_indicator_values(i)
                })
        
        return entry_signals

    def _format_price(self, price) -> Decimal:
        """Convert any numeric type to Decimal safely"""
        return Decimal(str(price))

    def _calculate_indicators(self) -> Dict:
        """Calculate all necessary technical indicators without TA-Lib"""
        df = self.price_data.copy()
        close_prices = df['close']
        
        # Calculate RSI
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        exp1 = close_prices.ewm(span=12, adjust=False).mean()
        exp2 = close_prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        
        # Calculate Bollinger Bands
        sma = close_prices.rolling(window=20).mean()
        rolling_std = close_prices.rolling(window=20).std()
        upper_band = sma + (rolling_std * 2)
        lower_band = sma - (rolling_std * 2)
        
        # Calculate Moving Averages
        ema_20 = close_prices.ewm(span=20, adjust=False).mean()
        sma_50 = close_prices.rolling(window=50).mean()
        
        return {
            'rsi': rsi,
            'macd': macd,
            'macd_signal': signal,
            'bbands': {
                'upper': upper_band,
                'middle': sma,
                'lower': lower_band
            },
            'ema_20': ema_20,
            'sma_50': sma_50
        }

    def _get_indicator_values(self, index: int) -> Dict:
        """Retrieve indicator values at a specific index"""
        return {
            'rsi': float(self.indicators['rsi'].iloc[index]),
            'macd': float(self.indicators['macd'].iloc[index]),
            'macd_signal': float(self.indicators['macd_signal'].iloc[index]),
            'bbands_lower': float(self.indicators['bbands']['lower'].iloc[index]),
            'ema_20': float(self.indicators['ema_20'].iloc[index]),
            'sma_50': float(self.indicators['sma_50'].iloc[index])
        }

    def get_latest_indicator_signals(self) -> Dict[str, bool]:
        """Get the latest indicator signals status"""
        latest_idx = -1
        
        # Get latest valid values
        rsi = self._format_price(self.indicators['rsi'].iloc[latest_idx])
        macd = self._format_price(self.indicators['macd'].iloc[latest_idx])
        macd_signal = self._format_price(self.indicators['macd_signal'].iloc[latest_idx])
        price = self._format_price(self.price_data['close'].iloc[latest_idx])
        bb_lower = self._format_price(self.indicators['bbands']['lower'].iloc[latest_idx])
        ema_20 = self._format_price(self.indicators['ema_20'].iloc[latest_idx])
        sma_50 = self._format_price(self.indicators['sma_50'].iloc[latest_idx])
        
        return {
            'rsi_oversold': rsi < Decimal('30'),
            'macd_bullish': macd > macd_signal,
            'price_below_bb': price < bb_lower,
            'ma_bullish': ema_20 > sma_50
        } 