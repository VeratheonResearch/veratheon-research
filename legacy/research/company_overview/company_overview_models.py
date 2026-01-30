from typing import Optional
from pydantic import BaseModel


class CompanyOverviewData(BaseModel):
    symbol: str
    asset_type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    cik: Optional[str] = None
    exchange: Optional[str] = None
    currency: Optional[str] = None
    country: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    address: Optional[str] = None
    fiscal_year_end: Optional[str] = None
    latest_quarter: Optional[str] = None
    market_capitalization: Optional[str] = None
    ebitda: Optional[str] = None
    pe_ratio: Optional[str] = None
    peg_ratio: Optional[str] = None
    book_value: Optional[str] = None
    dividend_per_share: Optional[str] = None
    dividend_yield: Optional[str] = None
    eps: Optional[str] = None
    revenue_per_share_ttm: Optional[str] = None
    profit_margin: Optional[str] = None
    operating_margin_ttm: Optional[str] = None
    return_on_assets_ttm: Optional[str] = None
    return_on_equity_ttm: Optional[str] = None
    revenue_ttm: Optional[str] = None
    gross_profit_ttm: Optional[str] = None
    diluted_eps_ttm: Optional[str] = None
    quarterly_earnings_growth_yoy: Optional[str] = None
    quarterly_revenue_growth_yoy: Optional[str] = None
    analyst_target_price: Optional[str] = None
    trailing_pe: Optional[str] = None
    forward_pe: Optional[str] = None
    price_to_sales_ratio_ttm: Optional[str] = None
    price_to_book_ratio: Optional[str] = None
    ev_to_revenue: Optional[str] = None
    ev_to_ebitda: Optional[str] = None
    beta: Optional[str] = None
    week_52_high: Optional[str] = None
    week_52_low: Optional[str] = None
    day_50_moving_average: Optional[str] = None
    day_200_moving_average: Optional[str] = None
    shares_outstanding: Optional[str] = None
    dividend_date: Optional[str] = None
    ex_dividend_date: Optional[str] = None


class CompanyOverviewAnalysis(BaseModel):
    symbol: str
    company_name: str
    sector: str
    industry: str
    market_cap_category: str
    business_description: str
    key_financials: str
    valuation_metrics: str
    profitability_assessment: str
    growth_indicators: str
    risk_factors: str
    competitive_position: str
    long_form_analysis: str