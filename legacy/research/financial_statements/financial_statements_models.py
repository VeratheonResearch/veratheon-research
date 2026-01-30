from typing import List, Dict, Any
from pydantic import BaseModel
import enum


class RevenueDriverTrend(str, enum.Enum):
    STRENGTHENING = "STRENGTHENING"
    WEAKENING = "WEAKENING"
    STABLE = "STABLE"
    VOLATILE = "VOLATILE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class CostStructureTrend(str, enum.Enum):
    IMPROVING_EFFICIENCY = "IMPROVING_EFFICIENCY"
    DETERIORATING_EFFICIENCY = "DETERIORATING_EFFICIENCY"
    STABLE_STRUCTURE = "STABLE_STRUCTURE"
    VOLATILE_COSTS = "VOLATILE_COSTS"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class WorkingCapitalTrend(str, enum.Enum):
    IMPROVING_MANAGEMENT = "IMPROVING_MANAGEMENT"
    DETERIORATING_MANAGEMENT = "DETERIORATING_MANAGEMENT"
    STABLE_MANAGEMENT = "STABLE_MANAGEMENT"
    CASH_FLOW_CONCERNS = "CASH_FLOW_CONCERNS"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class FinancialStatementsData(BaseModel):
    symbol: str
    income_statements: List[Dict[str, Any]]
    balance_sheets: List[Dict[str, Any]]
    cash_flow_statements: List[Dict[str, Any]]


class FinancialStatementsAnalysis(BaseModel):
    symbol: str
    revenue_driver_trend: RevenueDriverTrend
    revenue_driver_details: str
    cost_structure_trend: CostStructureTrend
    cost_structure_details: str
    working_capital_trend: WorkingCapitalTrend
    working_capital_details: str
    key_financial_changes: List[str]
    near_term_projection_risks: List[str]
    long_form_analysis: str
    critical_insights: str