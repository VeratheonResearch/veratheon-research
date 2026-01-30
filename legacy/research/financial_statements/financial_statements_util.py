import logging
from typing import Dict, Any, List
from src.lib.alpha_vantage_api import call_alpha_vantage_income_statement, call_alpha_vantage_balance_sheet, call_alpha_vantage_cash_flow
from legacy.research.financial_statements.financial_statements_models import FinancialStatementsData

log = logging.getLogger(__name__)


def get_financial_statements_data_for_symbol(symbol: str) -> FinancialStatementsData:
    """
    Calls Alpha Vantage APIs to fetch comprehensive financial statements data for analysis.
    
    Args:
        symbol: Stock symbol to research
    Returns:
        FinancialStatementsData containing income statements, balance sheets, and cash flow statements
    """
    try:
        # Get all three financial statements
        income_statement = call_alpha_vantage_income_statement(symbol)
        balance_sheet = call_alpha_vantage_balance_sheet(symbol)
        cash_flow = call_alpha_vantage_cash_flow(symbol)
        
        # Extract annual reports (focus on recent data - last 3 years)
        income_statements = income_statement.get('annualReports', [])[:3]
        balance_sheets = balance_sheet.get('annualReports', [])[:3]
        cash_flow_statements = cash_flow.get('annualReports', [])[:3]
        
        financial_data = FinancialStatementsData(
            symbol=symbol,
            income_statements=income_statements,
            balance_sheets=balance_sheets,
            cash_flow_statements=cash_flow_statements
        )
        
        log.info(f"Successfully retrieved financial statements data for {symbol}")
        return financial_data
        
    except Exception as e:
        log.error(f"Failed to get financial statements data for symbol: {symbol}. Error: {e}")
        # Return empty data structure to allow graceful handling
        return FinancialStatementsData(
            symbol=symbol,
            income_statements=[],
            balance_sheets=[],
            cash_flow_statements=[]
        )


def calculate_revenue_driver_metrics(income_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate metrics related to revenue drivers and trends.
    
    Args:
        income_statements: List of annual income statement data
    Returns:
        Dictionary containing revenue driver metrics and trends
    """
    if not income_statements or len(income_statements) < 2:
        return {
            "revenue_growth_rates": [],
            "revenue_trend": "INSUFFICIENT_DATA",
            "avg_growth_rate": 0.0,
            "revenue_volatility": 0.0,
            "years_analyzed": len(income_statements) if income_statements else 0
        }
    
    revenue_growth_rates = []
    revenues = []
    
    # Calculate revenue growth rates
    for i in range(len(income_statements) - 1):
        try:
            current_revenue = float(income_statements[i].get('totalRevenue', 0))
            previous_revenue = float(income_statements[i + 1].get('totalRevenue', 0))
            
            if previous_revenue == 0:
                continue
                
            growth_rate = ((current_revenue - previous_revenue) / previous_revenue) * 100
            revenue_growth_rates.append(growth_rate)
            revenues.append(current_revenue)
            
        except (ValueError, TypeError):
            continue
    
    if not revenue_growth_rates:
        return {
            "revenue_growth_rates": [],
            "revenue_trend": "INSUFFICIENT_DATA",
            "avg_growth_rate": 0.0,
            "revenue_volatility": 0.0,
            "years_analyzed": 0
        }
    
    avg_growth_rate = sum(revenue_growth_rates) / len(revenue_growth_rates)
    
    # Calculate volatility (standard deviation of growth rates)
    if len(revenue_growth_rates) > 1:
        variance = sum((x - avg_growth_rate) ** 2 for x in revenue_growth_rates) / len(revenue_growth_rates)
        volatility = variance ** 0.5
    else:
        volatility = 0.0
    
    # Determine trend
    if len(revenue_growth_rates) >= 2:
        recent_growth = revenue_growth_rates[0]  # Most recent
        older_growth = sum(revenue_growth_rates[1:]) / len(revenue_growth_rates[1:])
        
        if volatility > 15:  # High volatility threshold
            trend = "VOLATILE"
        elif recent_growth > older_growth + 2:  # Accelerating
            trend = "STRENGTHENING"
        elif recent_growth < older_growth - 2:  # Decelerating
            trend = "WEAKENING"
        else:
            trend = "STABLE"
    else:
        trend = "STABLE"
    
    return {
        "revenue_growth_rates": revenue_growth_rates,
        "revenue_trend": trend,
        "avg_growth_rate": avg_growth_rate,
        "revenue_volatility": volatility,
        "years_analyzed": len(revenue_growth_rates)
    }


def calculate_cost_structure_metrics(income_statements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate metrics related to cost structure efficiency and trends.
    
    Args:
        income_statements: List of annual income statement data
    Returns:
        Dictionary containing cost structure metrics and trends
    """
    if not income_statements or len(income_statements) < 2:
        return {
            "cogs_margins": [],
            "sga_ratios": [],
            "rd_ratios": [],
            "cost_trend": "INSUFFICIENT_DATA",
            "efficiency_score": 0.0,
            "years_analyzed": len(income_statements) if income_statements else 0
        }
    
    cogs_margins = []
    sga_ratios = []
    rd_ratios = []
    
    for statement in income_statements:
        try:
            total_revenue = float(statement.get('totalRevenue', 0))
            if total_revenue == 0:
                continue
            
            # Cost of goods sold margin (lower is better)
            cogs = float(statement.get('costOfRevenue', 0))
            cogs_margin = (cogs / total_revenue) * 100
            cogs_margins.append(cogs_margin)
            
            # SG&A as % of revenue (lower is generally better, but context matters)
            sga = float(statement.get('sellingGeneralAndAdministrative', 0))
            sga_ratio = (sga / total_revenue) * 100
            sga_ratios.append(sga_ratio)
            
            # R&D as % of revenue (context-dependent)
            rd = float(statement.get('researchAndDevelopment', 0))
            rd_ratio = (rd / total_revenue) * 100
            rd_ratios.append(rd_ratio)
            
        except (ValueError, TypeError, KeyError):
            continue
    
    if not cogs_margins:
        return {
            "cogs_margins": [],
            "sga_ratios": [],
            "rd_ratios": [],
            "cost_trend": "INSUFFICIENT_DATA",
            "efficiency_score": 0.0,
            "years_analyzed": 0
        }
    
    # Analyze trends (recent vs older periods)
    def analyze_cost_trend(ratios):
        if len(ratios) < 2:
            return "STABLE"
        
        recent_avg = sum(ratios[:1]) / 1 if len(ratios) >= 1 else 0  # Most recent
        older_avg = sum(ratios[1:]) / len(ratios[1:]) if len(ratios) > 1 else recent_avg
        
        # For cost ratios, lower is generally better (improved efficiency)
        if recent_avg < older_avg - 1:  # Costs decreasing as % of revenue
            return "IMPROVING_EFFICIENCY"
        elif recent_avg > older_avg + 1:  # Costs increasing as % of revenue
            return "DETERIORATING_EFFICIENCY"
        else:
            return "STABLE_STRUCTURE"
    
    cogs_trend = analyze_cost_trend(cogs_margins)
    sga_trend = analyze_cost_trend(sga_ratios)
    
    # Overall cost structure assessment
    improving_count = sum(1 for trend in [cogs_trend, sga_trend] if trend == "IMPROVING_EFFICIENCY")
    deteriorating_count = sum(1 for trend in [cogs_trend, sga_trend] if trend == "DETERIORATING_EFFICIENCY")
    
    if improving_count > deteriorating_count:
        overall_trend = "IMPROVING_EFFICIENCY"
    elif deteriorating_count > improving_count:
        overall_trend = "DETERIORATING_EFFICIENCY"
    else:
        overall_trend = "STABLE_STRUCTURE"
    
    # Calculate efficiency score (0-10, higher is better)
    # Based on recent cost ratios compared to historical averages
    efficiency_score = 5.0  # Neutral baseline
    if cogs_margins and len(cogs_margins) >= 2:
        if cogs_margins[0] < sum(cogs_margins[1:]) / len(cogs_margins[1:]):
            efficiency_score += 2
        elif cogs_margins[0] > sum(cogs_margins[1:]) / len(cogs_margins[1:]):
            efficiency_score -= 2
    
    return {
        "cogs_margins": cogs_margins,
        "sga_ratios": sga_ratios,
        "rd_ratios": rd_ratios,
        "cost_trend": overall_trend,
        "cogs_trend": cogs_trend,
        "sga_trend": sga_trend,
        "efficiency_score": max(0, min(10, efficiency_score)),
        "years_analyzed": len(cogs_margins)
    }


def calculate_working_capital_metrics(balance_sheets: List[Dict[str, Any]], cash_flows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate working capital management metrics and trends.
    
    Args:
        balance_sheets: List of annual balance sheet data
        cash_flows: List of annual cash flow data
    Returns:
        Dictionary containing working capital metrics and trends
    """
    if not balance_sheets or len(balance_sheets) < 2:
        return {
            "working_capital_ratios": [],
            "receivables_days": [],
            "inventory_days": [],
            "payables_days": [],
            "cash_conversion_cycle": [],
            "working_capital_trend": "INSUFFICIENT_DATA",
            "years_analyzed": len(balance_sheets) if balance_sheets else 0
        }
    
    working_capital_ratios = []
    receivables_days = []
    inventory_days = []
    payables_days = []
    cash_conversion_cycles = []
    
    for i, balance_sheet in enumerate(balance_sheets):
        try:
            total_assets = float(balance_sheet.get('totalAssets', 0))
            current_assets = float(balance_sheet.get('totalCurrentAssets', 0))
            current_liabilities = float(balance_sheet.get('totalCurrentLiabilities', 0))
            
            if total_assets == 0:
                continue
            
            # Working capital as % of total assets
            working_capital = current_assets - current_liabilities
            wc_ratio = (working_capital / total_assets) * 100
            working_capital_ratios.append(wc_ratio)
            
            # Calculate working capital components if available
            accounts_receivable = float(balance_sheet.get('currentAccountsReceivable', 0))
            inventory = float(balance_sheet.get('inventory', 0))
            accounts_payable = float(balance_sheet.get('currentAccountsPayable', 0))
            
            # For days calculations, we'd need revenue and COGS, but we'll use simplified ratios
            if current_assets > 0:
                receivables_ratio = (accounts_receivable / current_assets) * 100
                inventory_ratio = (inventory / current_assets) * 100
                receivables_days.append(receivables_ratio)
                inventory_days.append(inventory_ratio)
            
            if current_liabilities > 0:
                payables_ratio = (accounts_payable / current_liabilities) * 100
                payables_days.append(payables_ratio)
            
        except (ValueError, TypeError, KeyError):
            continue
    
    if not working_capital_ratios:
        return {
            "working_capital_ratios": [],
            "receivables_days": [],
            "inventory_days": [],
            "payables_days": [],
            "cash_conversion_cycle": [],
            "working_capital_trend": "INSUFFICIENT_DATA",
            "years_analyzed": 0
        }
    
    # Analyze working capital trend
    if len(working_capital_ratios) >= 2:
        recent_wc = working_capital_ratios[0]
        older_wc = sum(working_capital_ratios[1:]) / len(working_capital_ratios[1:])
        
        # Check for volatility
        if len(working_capital_ratios) > 2:
            wc_volatility = max(working_capital_ratios) - min(working_capital_ratios)
            if wc_volatility > 10:  # High volatility in working capital
                trend = "CASH_FLOW_CONCERNS"
            elif recent_wc > older_wc + 2:  # Improving working capital position
                trend = "IMPROVING_MANAGEMENT"
            elif recent_wc < older_wc - 2:  # Deteriorating working capital
                trend = "DETERIORATING_MANAGEMENT"
            else:
                trend = "STABLE_MANAGEMENT"
        else:
            trend = "STABLE_MANAGEMENT"
    else:
        trend = "STABLE_MANAGEMENT"
    
    return {
        "working_capital_ratios": working_capital_ratios,
        "receivables_days": receivables_days,
        "inventory_days": inventory_days,
        "payables_days": payables_days,
        "cash_conversion_cycle": cash_conversion_cycles,
        "working_capital_trend": trend,
        "years_analyzed": len(working_capital_ratios)
    }