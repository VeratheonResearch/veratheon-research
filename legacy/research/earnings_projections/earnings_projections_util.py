import logging
from typing import Dict, Any, List, Optional, Tuple
from src.lib.alpha_vantage_api import call_alpha_vantage_income_statement, call_alpha_vantage_overview, call_alpha_vantage_earnings_estimates
from src.lib.fiscal_year_utils import get_fiscal_year_info, get_appropriate_financial_data, log_fiscal_decision
from legacy.research.earnings_projections.earnings_projections_models import EarningsProjectionData

log = logging.getLogger(__name__)


def get_earnings_projection_data_for_symbol(
    symbol: str,
    historical_earnings_analysis: Optional[Dict[str, Any]] = None,
    financial_statements_analysis: Optional[Dict[str, Any]] = None
) -> EarningsProjectionData:
    """
    Fetches comprehensive data needed for earnings projections.
    Uses fiscal year timing to determine whether to focus on quarterly or annual data.

    Args:
        symbol: Stock symbol to research
        historical_earnings_analysis: Optional historical earnings analysis results
        financial_statements_analysis: Optional financial statements analysis results
    Returns:
        EarningsProjectionData containing all necessary data for projections
    """
    try:
        # Determine fiscal year timing and data selection strategy
        fiscal_info = log_fiscal_decision(symbol)

        # Get income statements
        income_statement = call_alpha_vantage_income_statement(symbol)
        overview = call_alpha_vantage_overview(symbol)

        # Select appropriate data based on fiscal timing
        if fiscal_info.use_annual_data:
            # Near fiscal year end - focus on annual data for stability
            quarterly_statements = income_statement.get('quarterlyReports', [])[:4]  # Last 4 quarters
            annual_statements = income_statement.get('annualReports', [])[:4]  # Last 4 years
            log.info(f"Using annual-focused data for {symbol} (near fiscal year end)")
        else:
            # Mid-year - focus on quarterly data for timeliness
            quarterly_statements = income_statement.get('quarterlyReports', [])[:8]  # Last 8 quarters
            annual_statements = income_statement.get('annualReports', [])[:3]  # Last 3 years
            log.info(f"Using quarterly-focused data for {symbol} (mid fiscal year)")
        
        projection_data = EarningsProjectionData(
            symbol=symbol,
            quarterly_income_statements=quarterly_statements,
            annual_income_statements=annual_statements,
            overview_data=overview,
            historical_earnings_analysis=historical_earnings_analysis,
            financial_statements_analysis=financial_statements_analysis
        )
        
        log.info(f"Successfully retrieved earnings projection data for {symbol}")
        return projection_data
        
    except Exception as e:
        log.error(f"Failed to get earnings projection data for symbol: {symbol}. Error: {e}")
        return EarningsProjectionData(
            symbol=symbol,
            quarterly_income_statements=[],
            annual_income_statements=[],
            overview_data={},
            historical_earnings_analysis=historical_earnings_analysis,
            financial_statements_analysis=financial_statements_analysis
        )


def calculate_revenue_projection_metrics(quarterly_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate revenue projection metrics based on historical quarterly data.
    
    Args:
        quarterly_statements: List of quarterly income statements
    Returns:
        Dictionary containing revenue projection metrics
    """
    if not quarterly_statements or len(quarterly_statements) < 4:
        return {
            "quarterly_revenues": [],
            "yoy_growth_rates": [],
            "qoq_growth_rates": [],
            "seasonal_factors": [],
            "avg_yoy_growth": 0.0,
            "revenue_trend": "INSUFFICIENT_DATA",
            "quarters_analyzed": len(quarterly_statements) if quarterly_statements else 0
        }
    
    quarterly_revenues = []
    yoy_growth_rates = []
    qoq_growth_rates = []
    
    # Extract revenues and calculate growth rates
    for i, statement in enumerate(quarterly_statements):
        try:
            revenue = float(statement.get('totalRevenue', 0))
            if revenue == 0:
                continue
                
            quarterly_revenues.append(revenue)
            
            # Calculate QoQ growth (quarter over quarter)
            if i > 0 and len(quarterly_revenues) > 1:
                prev_revenue = quarterly_revenues[-2]
                if prev_revenue > 0:
                    qoq_growth = ((revenue - prev_revenue) / prev_revenue) * 100
                    qoq_growth_rates.append(qoq_growth)
            
            # Calculate YoY growth (year over year, same quarter previous year)
            if i >= 4 and len(quarterly_revenues) >= 4:
                yoy_revenue = quarterly_revenues[-4]  # Same quarter last year
                if yoy_revenue > 0:
                    yoy_growth = ((revenue - yoy_revenue) / yoy_revenue) * 100
                    yoy_growth_rates.append(yoy_growth)
                    
        except (ValueError, TypeError):
            continue
    
    if not quarterly_revenues:
        return {
            "quarterly_revenues": [],
            "yoy_growth_rates": [],
            "qoq_growth_rates": [],
            "seasonal_factors": [],
            "avg_yoy_growth": 0.0,
            "revenue_trend": "INSUFFICIENT_DATA",
            "quarters_analyzed": 0
        }
    
    # Calculate seasonal factors (if we have enough data)
    seasonal_factors = []
    if len(quarterly_revenues) >= 8:  # At least 2 years of data
        # Calculate average revenue for each quarter position (Q1, Q2, Q3, Q4)
        quarter_positions = [[], [], [], []]
        for i, revenue in enumerate(quarterly_revenues):
            quarter_positions[i % 4].append(revenue)
        
        # Calculate seasonal factors (relative to average)
        total_avg = sum(quarterly_revenues) / len(quarterly_revenues)
        for position in quarter_positions:
            if position:
                position_avg = sum(position) / len(position)
                seasonal_factor = position_avg / total_avg if total_avg > 0 else 1.0
                seasonal_factors.append(seasonal_factor)
    
    avg_yoy_growth = sum(yoy_growth_rates) / len(yoy_growth_rates) if yoy_growth_rates else 0.0
    
    # Determine revenue trend
    if len(yoy_growth_rates) >= 2:
        recent_growth = sum(yoy_growth_rates[:2]) / 2  # Most recent 2 quarters
        older_growth = sum(yoy_growth_rates[2:]) / len(yoy_growth_rates[2:]) if len(yoy_growth_rates) > 2 else recent_growth
        
        if recent_growth > older_growth + 2:
            trend = "ACCELERATING"
        elif recent_growth < older_growth - 2:
            trend = "DECELERATING"
        elif avg_yoy_growth < 0:
            trend = "DECLINING"
        else:
            trend = "STABLE"
    else:
        trend = "STABLE"
    
    return {
        "quarterly_revenues": quarterly_revenues,
        "yoy_growth_rates": yoy_growth_rates,
        "qoq_growth_rates": qoq_growth_rates,
        "seasonal_factors": seasonal_factors,
        "avg_yoy_growth": avg_yoy_growth,
        "revenue_trend": trend,
        "quarters_analyzed": len(quarterly_revenues)
    }


def calculate_cost_structure_metrics(quarterly_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate cost structure metrics for projecting COGS and operating expenses.
    
    Args:
        quarterly_statements: List of quarterly income statements
    Returns:
        Dictionary containing cost structure metrics
    """
    if not quarterly_statements:
        return {
            "gross_margins": [],
            "cogs_ratios": [],
            "sga_ratios": [],
            "rd_ratios": [],
            "avg_gross_margin": 0.0,
            "avg_sga_ratio": 0.0,
            "avg_rd_ratio": 0.0,
            "cost_trend": "INSUFFICIENT_DATA",
            "quarters_analyzed": 0
        }
    
    gross_margins = []
    cogs_ratios = []
    sga_ratios = []
    rd_ratios = []
    
    for statement in quarterly_statements:
        try:
            revenue = float(statement.get('totalRevenue', 0))
            if revenue == 0:
                continue
            
            # Gross margin calculations
            cogs = float(statement.get('costOfRevenue', 0))
            gross_profit = float(statement.get('grossProfit', 0))
            
            if revenue > 0:
                cogs_ratio = (cogs / revenue) * 100
                gross_margin = (gross_profit / revenue) * 100
                cogs_ratios.append(cogs_ratio)
                gross_margins.append(gross_margin)
            
            # Operating expense ratios
            sga = float(statement.get('sellingGeneralAndAdministrative', 0))
            rd = float(statement.get('researchAndDevelopment', 0))
            
            if revenue > 0:
                sga_ratio = (sga / revenue) * 100
                rd_ratio = (rd / revenue) * 100
                sga_ratios.append(sga_ratio)
                rd_ratios.append(rd_ratio)
                
        except (ValueError, TypeError):
            continue
    
    if not gross_margins:
        return {
            "gross_margins": [],
            "cogs_ratios": [],
            "sga_ratios": [],
            "rd_ratios": [],
            "avg_gross_margin": 0.0,
            "avg_sga_ratio": 0.0,
            "avg_rd_ratio": 0.0,
            "cost_trend": "INSUFFICIENT_DATA",
            "quarters_analyzed": 0
        }
    
    # Calculate averages
    avg_gross_margin = sum(gross_margins) / len(gross_margins)
    avg_sga_ratio = sum(sga_ratios) / len(sga_ratios) if sga_ratios else 0.0
    avg_rd_ratio = sum(rd_ratios) / len(rd_ratios) if rd_ratios else 0.0
    
    # Determine cost trend
    if len(gross_margins) >= 4:
        recent_margin = sum(gross_margins[:2]) / 2  # Most recent 2 quarters
        older_margin = sum(gross_margins[2:4]) / 2  # Previous 2 quarters
        
        if recent_margin > older_margin + 1:  # Margin improving
            trend = "IMPROVING_EFFICIENCY"
        elif recent_margin < older_margin - 1:  # Margin deteriorating
            trend = "DETERIORATING_EFFICIENCY"
        else:
            trend = "STABLE_STRUCTURE"
    else:
        trend = "STABLE_STRUCTURE"
    
    return {
        "gross_margins": gross_margins,
        "cogs_ratios": cogs_ratios,
        "sga_ratios": sga_ratios,
        "rd_ratios": rd_ratios,
        "avg_gross_margin": avg_gross_margin,
        "avg_sga_ratio": avg_sga_ratio,
        "avg_rd_ratio": avg_rd_ratio,
        "cost_trend": trend,
        "quarters_analyzed": len(gross_margins)
    }


def calculate_profitability_metrics(quarterly_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate profitability metrics for tax rate and other bottom-line projections.
    
    Args:
        quarterly_statements: List of quarterly income statements
    Returns:
        Dictionary containing profitability metrics
    """
    if not quarterly_statements:
        return {
            "operating_margins": [],
            "tax_rates": [],
            "interest_expense_ratios": [],
            "avg_tax_rate": 0.0,
            "avg_operating_margin": 0.0,
            "avg_interest_ratio": 0.0,
            "quarters_analyzed": 0
        }
    
    operating_margins = []
    tax_rates = []
    interest_ratios = []
    
    for statement in quarterly_statements:
        try:
            revenue = float(statement.get('totalRevenue', 0))
            operating_income = float(statement.get('operatingIncome', 0))
            income_before_tax = float(statement.get('incomeBeforeTax', 0))
            tax_expense = float(statement.get('incomeTaxExpense', 0))
            interest_expense = float(statement.get('interestExpense', 0))
            
            if revenue > 0:
                operating_margin = (operating_income / revenue) * 100
                operating_margins.append(operating_margin)
                
                if interest_expense > 0:
                    interest_ratio = (interest_expense / revenue) * 100
                    interest_ratios.append(interest_ratio)
            
            if income_before_tax > 0 and tax_expense > 0:
                tax_rate = (tax_expense / income_before_tax) * 100
                tax_rates.append(tax_rate)
                
        except (ValueError, TypeError):
            continue
    
    return {
        "operating_margins": operating_margins,
        "tax_rates": tax_rates,
        "interest_expense_ratios": interest_ratios,
        "avg_tax_rate": sum(tax_rates) / len(tax_rates) if tax_rates else 25.0,  # Default 25% if no data
        "avg_operating_margin": sum(operating_margins) / len(operating_margins) if operating_margins else 0.0,
        "avg_interest_ratio": sum(interest_ratios) / len(interest_ratios) if interest_ratios else 0.0,
        "quarters_analyzed": len(quarterly_statements)
    }


def get_consensus_eps_estimate(symbol: str) -> Optional[float]:
    """
    Get consensus EPS estimate for comparison.
    
    Args:
        symbol: Stock symbol
    Returns:
        Consensus EPS estimate or None if not available
    """
    try:
        estimates_json = call_alpha_vantage_earnings_estimates(symbol)
        estimates = estimates_json.get('estimates', [])
        
        if estimates:
            # Look for next quarter estimate
            for estimate in estimates:
                if estimate.get('horizon') == 'next fiscal quarter':
                    eps_estimate = estimate.get('eps_estimate_average')
                    if eps_estimate and eps_estimate != "Not enough consensus":
                        return float(eps_estimate)
            
            # Fallback to first available estimate
            first_estimate = estimates[0].get('eps_estimate_average')
            if first_estimate and first_estimate != "Not enough consensus":
                return float(first_estimate)
        
        return None
        
    except Exception as e:
        log.warning(f"Could not get consensus EPS estimate for {symbol}: {e}")
        return None


def project_next_quarter_revenue(revenue_metrics: Dict[str, Any], base_revenue: float) -> Tuple[float, str]:
    """
    Project next quarter revenue using historical patterns.
    
    Args:
        revenue_metrics: Revenue metrics from calculate_revenue_projection_metrics
        base_revenue: Most recent quarter revenue as baseline
    Returns:
        Tuple of (projected_revenue, methodology_description)
    """
    if not revenue_metrics or revenue_metrics.get("quarters_analyzed", 0) < 2:
        return base_revenue * 1.02, "SIMPLE_GROWTH_ASSUMPTION"  # 2% default growth
    
    yoy_growth_rates = revenue_metrics.get("yoy_growth_rates", [])
    seasonal_factors = revenue_metrics.get("seasonal_factors", [])
    avg_yoy_growth = revenue_metrics.get("avg_yoy_growth", 0.0)
    
    # Use YoY growth if available
    if yoy_growth_rates:
        recent_yoy_growth = sum(yoy_growth_rates[:2]) / 2 if len(yoy_growth_rates) >= 2 else yoy_growth_rates[0]
        
        # Apply seasonal adjustment if available
        if seasonal_factors and len(seasonal_factors) == 4:
            next_quarter_position = 0  # Assuming Q1 as next (can be made dynamic)
            seasonal_factor = seasonal_factors[next_quarter_position]
            
            # Calculate seasonal-adjusted projection
            base_projected = base_revenue * (1 + recent_yoy_growth / 100)
            projected_revenue = base_projected * seasonal_factor
            methodology = "SEASONAL_ADJUSTMENT"
        else:
            # Simple YoY growth application
            projected_revenue = base_revenue * (1 + recent_yoy_growth / 100)
            methodology = "GROWTH_RATE_EXTRAPOLATION"
    else:
        # Fallback to trend-based projection
        if avg_yoy_growth > 0:
            projected_revenue = base_revenue * (1 + avg_yoy_growth / 100)
            methodology = "HISTORICAL_TREND"
        else:
            projected_revenue = base_revenue * 1.02  # Conservative 2% growth
            methodology = "CONSERVATIVE_ASSUMPTION"
    
    return projected_revenue, methodology