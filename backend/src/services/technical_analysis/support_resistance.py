from .base import BaseTechnicalAnalysis
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema, find_peaks
from typing import List, Tuple, Dict
from decimal import Decimal

class SupportResistanceAnalyzer(BaseTechnicalAnalysis):
    def __init__(self, price_data: pd.DataFrame, window: int = 5):
        super().__init__(price_data)
        self.window = window
        self.price_series = price_data['close']

    def find_levels(self) -> Tuple[List[float], List[float]]:
        """Find support and resistance levels using local extrema"""
        try:
            if len(self.price_series) < self.window * 2:
                return [], []
                
            # Find local minima and maxima with smaller window
            local_min = self._find_local_minima()
            local_max = self._find_local_maxima()
            
            # Use tighter threshold for clustering
            support_levels = self._cluster_levels(local_min, threshold=0.005)
            resistance_levels = self._cluster_levels(local_max, threshold=0.005)
            
            # Filter levels near current price
            current_price = float(self.price_series.iloc[-1])
            
            # Use percentage-based filtering
            support_levels = [level for level in support_levels 
                             if level < current_price * 0.99]  # Within 1% below
            resistance_levels = [level for level in resistance_levels 
                               if level > current_price * 1.01]  # Within 1% above
            
            # Ensure we have at least some levels with tighter ranges
            if not support_levels:
                support_levels = [
                    current_price * 0.99,
                    current_price * 0.95,
                    current_price * 0.90
                ]
            if not resistance_levels:
                resistance_levels = [
                    current_price * 1.01,
                    current_price * 1.05,
                    current_price * 1.10
                ]
            
            return support_levels[:3], resistance_levels[:3]
            
        except Exception as e:
            print(f"[Analysis] ⚠️ Error finding S/R levels: {str(e)}")
            return [], []
            
    def _find_local_minima(self) -> np.ndarray:
        """Find local minimum points"""
        return self.price_series.iloc[argrelextrema(
            self.price_series.values, 
            np.less_equal,
            order=self.window
        )[0]].values
        
    def _find_local_maxima(self) -> np.ndarray:
        """Find local maximum points"""
        return self.price_series.iloc[argrelextrema(
            self.price_series.values, 
            np.greater_equal,
            order=self.window
        )[0]].values
        
    def _cluster_levels(self, levels: np.ndarray, threshold: float = 0.01) -> List[float]:
        """Cluster nearby levels together"""
        if len(levels) == 0:
            return []
            
        # Sort levels
        sorted_levels = np.sort(levels)
        clusters = []
        current_cluster = [sorted_levels[0]]
        
        # Group nearby levels
        for level in sorted_levels[1:]:
            if abs(level - np.mean(current_cluster)) / np.mean(current_cluster) <= threshold:
                current_cluster.append(level)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
                
        clusters.append(np.mean(current_cluster))
        
        return clusters 

    def calculate_entry_points(self, support_levels: List[float], resistance_levels: List[float]) -> List[Dict]:
        """Calculate optimal entry points based on technical levels"""
        current_price = self._format_price(self.price_data['close'].iloc[-1])
        entry_points = []
        
        # Add support levels as entry points
        for level in support_levels:
            level_dec = self._format_price(level)
            if level_dec < current_price:
                percentage = (current_price - level_dec) / current_price * Decimal('100')
                entry_points.append({
                    "price": float(level_dec),
                    "percentage": float(percentage),
                    "timestamp": None
                })
        
        # Add weighted average entries
        ma_20 = self._format_price(self.price_data['close'].rolling(window=20).mean().iloc[-1])
        ma_50 = self._format_price(self.price_data['close'].rolling(window=50).mean().iloc[-1])
        
        if ma_20 < current_price:
            percentage = (current_price - ma_20) / current_price * Decimal('100')
            entry_points.append({
                "price": float(ma_20),
                "percentage": float(percentage),
                "timestamp": None
            })
        
        return sorted(entry_points, key=lambda x: x['price'])