from pydantic import BaseModel, Field
from typing import Optional

class TokenAnalysisRequest(BaseModel):
    contract_address: str = Field(..., description="Ethereum token contract address")
    timeframe: str = Field(..., description="Timeframe for analysis (e.g., '15m', '1h', '4h', '1d')")
    interval_days: int = Field(default=30, description="Number of days to analyze")
    investment_amount: float = Field(default=100.0, description="Amount to invest in the token")

class SentimentAnalysisRequest(BaseModel):
    telegram_channel: str = Field(..., description="Telegram channel URL to analyze")
    interval_days: int = Field(default=30, description="Number of days of messages to analyze") 