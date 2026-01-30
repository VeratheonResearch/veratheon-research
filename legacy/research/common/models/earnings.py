from typing import List, Optional
from pydantic import BaseModel

class RawEarnings(BaseModel):
    symbol: str
    annual_earnings: List
    quarterly_earnings: List


class EarningsEstimate(BaseModel):
    """Model for individual earnings estimate from Earnings Estimates API."""
    date: str
    horizon: str
    eps_estimate_average: str
    eps_estimate_high: Optional[str] = None
    eps_estimate_low: Optional[str] = None
    eps_estimate_analyst_count: Optional[str] = None
    eps_estimate_average_7_days_ago: Optional[str] = None
    eps_estimate_average_30_days_ago: Optional[str] = None
    eps_estimate_average_60_days_ago: Optional[str] = None
    eps_estimate_average_90_days_ago: Optional[str] = None
    eps_estimate_revision_up_trailing_7_days: Optional[str] = None
    eps_estimate_revision_down_trailing_7_days: Optional[str] = None
    eps_estimate_revision_up_trailing_30_days: Optional[str] = None
    eps_estimate_revision_down_trailing_30_days: Optional[str] = None
    revenue_estimate_average: Optional[str] = None
    revenue_estimate_high: Optional[str] = None
    revenue_estimate_low: Optional[str] = None
    revenue_estimate_analyst_count: Optional[str] = None

class RawEarningsEstimates(BaseModel):
    """Model for Earnings Estimates API response."""
    symbol: str
    estimates: List[EarningsEstimate]

class RawGlobalQuote(BaseModel):
    symbol: str
    open: str
    high: str
    low: str
    price: str
    volume: str
    latest_trading_day: str
    previous_close: str
    change: str
    change_percent: str