from typing import Dict
from decimal import Decimal

def calculate_risk_score(technical_analysis: Dict) -> float:
    """Calculate risk score based on technical indicators"""
    rsi = Decimal(str(technical_analysis['rsi']))
    volatility = Decimal(str(technical_analysis['volatility']))
    
    # RSI risk component (higher RSI = higher risk)
    rsi_risk = (rsi / Decimal('100')) * Decimal('0.4')  # 40% weight
    
    # Volatility risk component
    volatility_risk = min(volatility * Decimal('2'), Decimal('1')) * Decimal('0.4')  # 40% weight
    
    # Support/Resistance risk component
    support_count = Decimal(str(len(technical_analysis['support_levels'])))
    resistance_count = Decimal(str(len(technical_analysis['resistance_levels'])))
    price_levels_risk = resistance_count / (support_count + Decimal('1')) * Decimal('0.2')  # 20% weight
    
    return float(round(rsi_risk + volatility_risk + price_levels_risk, 2))

def calculate_expected_return(entry_points: list, exit_points: list) -> float:
    """Calculate expected return based on entry and exit points"""
    if not entry_points or not exit_points:
        return 0.0
        
    avg_entry = Decimal(str(sum(ep['price'] for ep in entry_points))) / Decimal(str(len(entry_points)))
    avg_exit = Decimal(str(sum(ep['price'] for ep in exit_points))) / Decimal(str(len(exit_points)))
    
    return float(round(((avg_exit - avg_entry) / avg_entry) * Decimal('100'), 2))