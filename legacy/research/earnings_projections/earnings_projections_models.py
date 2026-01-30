from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import enum


class RevenueProjectionMethod(str, enum.Enum):
    HISTORICAL_TREND = "HISTORICAL_TREND"
    SEASONAL_ADJUSTMENT = "SEASONAL_ADJUSTMENT"
    GROWTH_RATE_EXTRAPOLATION = "GROWTH_RATE_EXTRAPOLATION"
    MIXED_METHODOLOGY = "MIXED_METHODOLOGY"


class CostProjectionMethod(str, enum.Enum):
    MARGIN_BASED = "MARGIN_BASED"
    PERCENTAGE_OF_REVENUE = "PERCENTAGE_OF_REVENUE"
    HISTORICAL_TREND = "HISTORICAL_TREND"
    MIXED_METHODOLOGY = "MIXED_METHODOLOGY"


class EarningsProjectionData(BaseModel):
    symbol: str
    quarterly_income_statements: List[Dict[str, Any]]
    annual_income_statements: List[Dict[str, Any]]
    overview_data: Dict[str, Any]
    historical_earnings_analysis: Optional[Dict[str, Any]] = None
    financial_statements_analysis: Optional[Dict[str, Any]] = None


class NextQuarterProjection(BaseModel):
    """Independent projection for next quarter's key line items"""
    
    # Revenue Projection
    projected_revenue: float
    revenue_projection_method: RevenueProjectionMethod
    revenue_reasoning: str
    
    # Cost Projections
    projected_cogs: float
    cogs_projection_method: CostProjectionMethod
    cogs_reasoning: str
    
    projected_gross_profit: float
    projected_gross_margin: float
    
    # Operating Expense Projections
    projected_sga: float
    sga_reasoning: str
    projected_rd: float
    rd_reasoning: str
    projected_total_opex: float
    
    # Bottom Line Projections
    projected_operating_income: float
    projected_operating_margin: float
    
    projected_interest_expense: float
    projected_tax_expense: float
    projected_tax_rate: float
    
    projected_net_income: float
    projected_eps: float
    
    # Comparison with Consensus
    consensus_eps_estimate: Optional[float] = None
    eps_vs_consensus_diff: Optional[float] = None
    eps_vs_consensus_percent: Optional[float] = None


class EarningsProjectionAnalysis(BaseModel):
    symbol: str
    next_quarter_projection: NextQuarterProjection
    projection_methodology: str
    key_assumptions: List[str]
    upside_risks: List[str]
    downside_risks: List[str]
    data_quality_score: int
    consensus_validation_summary: str
    long_form_analysis: str
    critical_insights: str