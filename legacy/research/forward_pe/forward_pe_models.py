from typing import List, Dict, Any
from pydantic import BaseModel
import enum


class ValuationConfidence(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ValuationAttractiveness(str, enum.Enum):
    UNDERVALUED = "UNDERVALUED"
    FAIRLY_VALUED = "FAIRLY_VALUED"
    OVERVALUED = "OVERVALUED"
    EXTREME_VALUATION = "EXTREME_VALUATION"


class EarningsQuality(str, enum.Enum):
    HIGH_QUALITY = "HIGH_QUALITY"
    ADEQUATE_QUALITY = "ADEQUATE_QUALITY"
    QUESTIONABLE_QUALITY = "QUESTIONABLE_QUALITY"
    POOR_QUALITY = "POOR_QUALITY"

class ForwardPEEarningsSummary(BaseModel):
    symbol: str
    overview: Dict[str, Any]
    current_price: str
    quarterly_earnings: List
    consensus_eps_next_quarter: str

class ForwardPeValuation(BaseModel):
    symbol: str
    current_price: float
    forward_pe_ratio: float
    sector_average_pe: float
    historical_pe_range: str
    valuation_attractiveness: ValuationAttractiveness
    earnings_quality: EarningsQuality
    confidence: ValuationConfidence
    long_form_analysis: str
    critical_insights: str

class ForwardPeSanityCheckRealistic(str, enum.Enum):
    REALISTIC = "REALISTIC"
    PLAUSIBLE = "PLAUSIBLE"
    NOT_REALISTIC = "NOT_REALISTIC"

class ForwardPeSanityCheck(BaseModel):
    symbol: str
    earnings_data_quality: EarningsQuality
    consensus_reliability: ValuationConfidence
    long_form_analysis: str
    is_realistic: ForwardPeSanityCheckRealistic
    critical_insights: str