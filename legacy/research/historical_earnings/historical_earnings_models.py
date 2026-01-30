from typing import List, Dict, Any
from pydantic import BaseModel
import enum


class EarningsPattern(str, enum.Enum):
    CONSISTENT_BEATS = "CONSISTENT_BEATS"
    CONSISTENT_MISSES = "CONSISTENT_MISSES"
    MIXED_PATTERN = "MIXED_PATTERN"
    VOLATILE = "VOLATILE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class RevenueGrowthTrend(str, enum.Enum):
    ACCELERATING = "ACCELERATING"
    DECELERATING = "DECELERATING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"
    VOLATILE = "VOLATILE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class MarginTrend(str, enum.Enum):
    IMPROVING = "IMPROVING"
    DETERIORATING = "DETERIORATING"
    STABLE = "STABLE"
    VOLATILE = "VOLATILE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class HistoricalEarningsData(BaseModel):
    symbol: str
    quarterly_earnings: List[Dict[str, Any]]
    annual_earnings: List[Dict[str, Any]]
    income_statement: List[Dict[str, Any]]


class HistoricalEarningsAnalysis(BaseModel):
    symbol: str
    earnings_pattern: EarningsPattern
    earnings_pattern_details: str
    revenue_growth_trend: RevenueGrowthTrend
    revenue_growth_details: str
    margin_trend: MarginTrend
    margin_trend_details: str
    key_insights: List[str]
    long_form_analysis: str
    critical_insights: str