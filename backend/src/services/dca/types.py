from typing import TypedDict, List
from datetime import datetime

class Trade(TypedDict):
    entry_date: datetime
    exit_date: datetime
    entry_price: float
    exit_price: float
    quantity: float
    return_pct: float
    profit_loss: float

class BacktestResults(TypedDict):
    historical_performance: float
    win_rate: float
    average_return: float
    max_drawdown: float
    risk_adjusted_return: float 