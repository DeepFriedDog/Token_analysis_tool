from typing import List, Dict
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP

class DCACalculator:
    def __init__(self, price_data: pd.DataFrame, investment_amount: Decimal):
        self.price_data = price_data
        self.total_investment = investment_amount
        
    def _format_price(self, price) -> Decimal:
        """Convert any numeric type to Decimal safely"""
        return Decimal(str(price))
        
    def calculate_entry_points(self, support_levels: List[float], resistance_levels: List[float]) -> List[Dict]:
        """Calculate optimal entry points based on technical levels"""
        try:
            current_price = self._format_price(self.price_data['close'].iloc[-1])
            entry_points = []
            
            # Convert support_levels and resistance_levels to Decimal
            decimal_support_levels = [self._format_price(level) for level in support_levels]
            decimal_resistance_levels = [self._format_price(level) for level in resistance_levels]
            
            # Calculate entry points based on support levels
            total_strength = Decimal('0')
            preliminary_points = []
            
            for level in decimal_support_levels:
                if level < current_price:
                    percentage = ((current_price - level) / current_price) * Decimal('100')
                    strength = self._calculate_level_strength(level, decimal_support_levels)
                    total_strength += strength
                    
                    preliminary_points.append({
                        "price": level,
                        "percentage": percentage,
                        "strength": strength
                    })
            
            # Calculate position sizes based on strength
            if total_strength > Decimal('0'):
                for point in preliminary_points:
                    position_size = (self.total_investment * point["strength"]) / total_strength
                    position_size = position_size.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    
                    entry_points.append({
                        "price": float(point["price"]),
                        "percentage": float(point["percentage"].quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                        "position_size": float(position_size),
                        "strength": float(point["strength"])
                    })
            
            # Calculate volatility using Decimal
            pct_changes = []
            close_prices = self.price_data['close'].values
            for i in range(1, len(close_prices)):
                prev_price = self._format_price(close_prices[i-1])
                curr_price = self._format_price(close_prices[i])
                if prev_price > Decimal('0'):
                    pct_change = (curr_price - prev_price) / prev_price
                    pct_changes.append(float(pct_change))
            
            volatility_std = Decimal(str(pd.Series(pct_changes).std()))
            volatility = (volatility_std * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            volatility_entries = self._calculate_volatility_based_entries(current_price, volatility)
            
            # Add volatility-based entries
            for entry in volatility_entries:
                entry_points.append({
                    "price": float(entry["price"]),
                    "percentage": float(entry["percentage"]),
                    "position_size": float(entry["position_size"]),
                    "strength": float(entry["strength"])
                })
            
            return sorted(entry_points, key=lambda x: x["price"])
            
        except Exception as e:
            print(f"[DCA] ❌ Error calculating entry points: {str(e)}")
            return []
        
    def _calculate_level_strength(self, level: Decimal, support_levels: List[Decimal]) -> Decimal:
        """Calculate the strength of a support level"""
        strength = Decimal('1.0')
        cluster_threshold = Decimal('0.02')  # 2% threshold for clustering
        
        for other_level in support_levels:
            if abs(level - other_level) / level < cluster_threshold:
                strength += Decimal('0.5')
                
        return strength
    
    def _calculate_volatility_based_entries(self, current_price: Decimal, volatility: Decimal) -> List[Dict]:
        """Calculate additional entry points based on volatility"""
        entries = []
        volatility_levels = [Decimal('1.0'), Decimal('1.5'), Decimal('2.0')]  # Multiples of volatility
        
        for vol_multiple in volatility_levels:
            # Calculate price drop: (current_price * volatility * vol_multiple) / 100
            price_drop = (current_price * volatility * vol_multiple) / Decimal('100')
            entry_price = current_price - price_drop
            
            percentage = ((current_price - entry_price) / current_price) * Decimal('100')
            percentage = percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Calculate position size: total_investment / (number of entries + existing entry points)
            total_entries = Decimal(str(len(volatility_levels)))
            position_size = (self.total_investment / total_entries).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            # Strength: 1 / vol_multiple
            strength = (Decimal('1') / vol_multiple).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            entries.append({
                "price": entry_price,
                "percentage": percentage,
                "position_size": position_size,
                "strength": strength,
                "timestamp": None
            })
        
        return entries
    
    def calculate_exit_points(self, resistance_levels: List[float], fibonacci_levels: List[Dict]) -> List[Dict]:
        """Calculate exit points based on resistance and Fibonacci levels"""
        current_price = self._format_price(self.price_data['close'].iloc[-1])
        exit_points = []
        
        for level in resistance_levels:
            level_dec = self._format_price(level)
            if level_dec > current_price:
                percentage = ((level_dec - current_price) / current_price) * Decimal('100')
                exit_points.append({
                    "price": float(level_dec),
                    "percentage": float(percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    "type": "resistance"
                })
        
        for fib in fibonacci_levels:
            fib_price = self._format_price(fib['price'])
            if fib_price > current_price and fib['level'] > Decimal('1'):
                percentage = ((fib_price - current_price) / current_price) * Decimal('100')
                exit_points.append({
                    "price": float(fib_price),
                    "percentage": float(percentage.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                    "type": f"fibonacci_{fib['level']}"
                })
        
        return sorted(exit_points, key=lambda x: x['price'])
    
    def distribute_investment(self, entry_points: List[Dict]) -> List[Dict]:
        """Distribute investment amount across entry points"""
        if not entry_points:
            return []
            
        # Weight distribution based on price levels
        total_weight = sum(1 / ep['price'] for ep in entry_points)
        distribution = []
        
        for entry in entry_points:
            weight = (1 / entry['price']) / total_weight
            amount = self.total_investment * weight
            distribution.append({
                "amount": round(amount, 2),
                "price_target": entry['price'],
                "timestamp": entry.get('timestamp')
            })
        
        return distribution 
    
    def calculate_volatility(self) -> Decimal:
        """Calculate price volatility using standard deviation of percentage changes"""
        try:
            pct_changes = []
            close_prices = self.price_data['close'].values
            for i in range(1, len(close_prices)):
                prev_price = self._format_price(close_prices[i-1])
                curr_price = self._format_price(close_prices[i])
                if prev_price > Decimal('0'):
                    pct_change = (curr_price - prev_price) / prev_price
                    pct_changes.append(float(pct_change))
            
            volatility_std = Decimal(str(pd.Series(pct_changes).std()))
            return (volatility_std * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            print(f"[DCA] ❌ Error calculating volatility: {str(e)}")
            return Decimal('0') 