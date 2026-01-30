from pydantic import BaseModel
from typing import List
import enum


class TradeDirection(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"
    COMPLEX = "COMPLEX"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class TimeHorizon(str, enum.Enum):
    SHORT_TERM = "SHORT_TERM"  # < 3 months
    MEDIUM_TERM = "MEDIUM_TERM"  # 3-12 months
    LONG_TERM = "LONG_TERM"  # > 12 months


class TradeConfidence(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    SPECULATIVE = "SPECULATIVE"

class TradeIdea(BaseModel):
    symbol: str
    trade_direction: TradeDirection
    time_horizon: TimeHorizon
    risk_level: RiskLevel
    overall_confidence: TradeConfidence
    
    # Trade specifics
    high_level_trade_idea: str
    reasoning: str
    key_catalysts: List[str]
    risk_factors: List[str]
    
    # Implementation details
    simple_equity_trade_specifics: str
    option_play: str
    risk_hedge: str
    
    # Price targets and stops
    entry_price_target: str
    upside_price_target: str
    downside_stop_loss: str
    
    critical_insights: str
    