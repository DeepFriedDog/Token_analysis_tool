import numpy as np
import pandas as pd
from typing import Tuple

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    # Calculate price changes
    delta = prices.diff()
    
    # Separate gains and losses
    gains = delta.where(delta > 0, 0)
    losses = -delta.where(delta < 0, 0)
    
    # Calculate average gains and losses
    avg_gains = gains.rolling(window=period).mean()
    avg_losses = losses.rolling(window=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_volatility(prices: pd.Series, period: int = 14) -> float:
    """Calculate price volatility using standard deviation of returns"""
    # Fill NA values using forward fill
    clean_prices = prices.ffill()
    returns = clean_prices.pct_change(fill_method=None)
    volatility = returns.std()
    return volatility

def calculate_moving_averages(prices: pd.Series) -> Tuple[pd.Series, pd.Series]:
    """Calculate short and long-term moving averages"""
    sma_20 = prices.rolling(window=20).mean()
    sma_50 = prices.rolling(window=50).mean()
    return sma_20, sma_50

def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate Bollinger Bands"""
    middle_band = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return upper_band, middle_band, lower_band 