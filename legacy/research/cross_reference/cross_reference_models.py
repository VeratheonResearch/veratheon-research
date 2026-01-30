
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from legacy.research.forward_pe.forward_pe_models import ForwardPeValuation
from legacy.research.news_sentiment.news_sentiment_models import NewsSentimentSummary
from legacy.research.historical_earnings.historical_earnings_models import HistoricalEarningsAnalysis
from legacy.research.financial_statements.financial_statements_models import FinancialStatementsAnalysis
from legacy.research.earnings_projections.earnings_projections_models import EarningsProjectionAnalysis
from legacy.research.management_guidance.management_guidance_models import ManagementGuidanceAnalysis

class Flows(str, Enum):
    HISTORICAL_EARNINGS = "historical_earnings"
    FINANCIAL_STATEMENTS = "financial_statements"
    EARNINGS_PROJECTIONS = "earnings_projections"
    MANAGEMENT_GUIDANCE = "management_guidance"
    FORWARD_PE = "forward_pe"
    NEWS_SENTIMENT = "news_sentiment"

class MajorAdjustment(BaseModel):
    analysis_types_causing_discrepancy: List[Flows]
    adjustment_analysis: str
    adjustment_reasoning: str

class MinorAdjustment(BaseModel):
    analysis_types_causing_discrepancy: List[Flows]
    adjustment_analysis: str
    adjustment_reasoning: str

class CrossReferencedAnalysis(BaseModel):
    major_adjustments: Optional[List[MajorAdjustment]]
    minor_adjustments: Optional[List[MinorAdjustment]]

class CrossReferencedAnalysisCompletion(BaseModel):
    original_analysis_type: Flows
    cross_referenced_analysis: CrossReferencedAnalysis
