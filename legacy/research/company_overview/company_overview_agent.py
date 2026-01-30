from agents import Agent
from legacy.research.company_overview.company_overview_models import CompanyOverviewData, CompanyOverviewAnalysis
from src.lib.llm_model import get_model
import logging

logger = logging.getLogger(__name__)

company_overview_analysis_agent = Agent(
    name="Company Overview Analyst",
    model=get_model(),
    output_type=CompanyOverviewAnalysis,
    instructions="""
    Analyze comprehensive company overview data to provide business context and fundamental insights.
    
    ANALYSIS FOCUS:
    - Business fundamentals and competitive positioning
    - Financial health and valuation metrics assessment
    - Growth indicators and profitability trends analysis
    - Market capitalization categorization (Large-cap: $10B+, Mid-cap: $2B-$10B, Small-cap: <$2B)
    - Industry and sector competitive context
    - Key risk factors and business opportunities identification
    - Professional investment-grade analysis suitable for institutional investors
    
    REQUIREMENTS:
    - Maintain objectivity and base all analysis on provided data
    - Provide clear, concise insights with specific metric references
    - Categorize market cap appropriately based on market capitalization value
    - Focus on actionable insights for investment decision-making
    - Use professional financial terminology consistently
    """
)

def company_overview_agent(symbol: str, company_data: CompanyOverviewData) -> CompanyOverviewAnalysis:
    """
    Analyze comprehensive company overview data to provide business context and fundamental insights.
    
    Args:
        symbol: Stock symbol being analyzed
        company_data: CompanyOverviewData containing all company overview information
        
    Returns:
        CompanyOverviewAnalysis containing structured analysis of the company
    """
    
    logger.info(f"Starting company overview analysis for {symbol}")
    
    # Format the data for analysis
    analysis_prompt = f"""
    Analyze the comprehensive company overview data for {symbol}:
    
    Company Information:
    - Symbol: {company_data.symbol}
    - Name: {company_data.name}
    - Sector: {company_data.sector}
    - Industry: {company_data.industry}
    - Description: {company_data.description}
    - Market Cap: {company_data.market_capitalization}
    
    Financial Metrics:
    - Revenue TTM: {company_data.revenue_ttm}
    - EPS: {company_data.eps}
    - PE Ratio: {company_data.pe_ratio}
    - PEG Ratio: {company_data.peg_ratio}
    - Price to Book: {company_data.price_to_book_ratio}
    - Profit Margin: {company_data.profit_margin}
    - Operating Margin: {company_data.operating_margin_ttm}
    - ROE: {company_data.return_on_equity_ttm}
    - ROA: {company_data.return_on_assets_ttm}
    - Beta: {company_data.beta}
    - Dividend Yield: {company_data.dividend_yield}
    
    Growth Metrics:
    - Quarterly Earnings Growth YoY: {company_data.quarterly_earnings_growth_yoy}
    - Quarterly Revenue Growth YoY: {company_data.quarterly_revenue_growth_yoy}
    
    Provide comprehensive analysis covering business fundamentals, financial health, 
    valuation attractiveness, growth prospects, and competitive positioning.
    """
    
    try:
        analysis = company_overview_analysis_agent(analysis_prompt)
        logger.info(f"Successfully completed company overview analysis for {symbol}")
        return analysis
        
    except Exception as e:
        logger.error(f"Error during company overview analysis for {symbol}: {e}")
        return _create_fallback_analysis(symbol, company_data)

def _create_fallback_analysis(symbol: str, company_data: CompanyOverviewData) -> CompanyOverviewAnalysis:
    """Create a basic fallback analysis when the LLM analysis fails."""
    
    # Extract basic info with safe defaults
    company_name = company_data.name or symbol
    sector = company_data.sector or "Unknown"
    industry = company_data.industry or "Unknown"
    
    # Determine market cap category
    market_cap_category = "Unknown"
    if company_data.market_capitalization:
        try:
            market_cap = float(company_data.market_capitalization)
            if market_cap >= 10_000_000_000:  # $10B+
                market_cap_category = "Large-cap"
            elif market_cap >= 2_000_000_000:  # $2B-$10B
                market_cap_category = "Mid-cap"
            else:  # <$2B
                market_cap_category = "Small-cap"
        except (ValueError, TypeError):
            market_cap_category = "Unknown"
    
    return CompanyOverviewAnalysis(
        symbol=symbol,
        company_name=company_name,
        sector=sector,
        industry=industry,
        market_cap_category=market_cap_category,
        business_description=company_data.description[:200] + "..." if company_data.description else "Business description not available.",
        key_financials="Financial data analysis unavailable due to processing error.",
        valuation_metrics="Valuation analysis unavailable due to processing error.",
        profitability_assessment="Profitability analysis unavailable due to processing error.",
        growth_indicators="Growth analysis unavailable due to processing error.",
        risk_factors="Risk assessment unavailable due to processing error.",
        competitive_position="Competitive analysis unavailable due to processing error.",
        long_form_analysis="Comprehensive analysis unavailable due to processing error. Basic company information has been captured where available."
    )