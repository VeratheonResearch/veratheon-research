import logging
from typing import Dict, Any
from src.lib.alpha_vantage_api import call_alpha_vantage_earnings, call_alpha_vantage_income_statement
from legacy.research.historical_earnings.historical_earnings_models import HistoricalEarningsData
from legacy.research.common.models.earnings import RawEarnings

log = logging.getLogger(__name__)


def get_historical_earnings_data_for_symbol(symbol: str) -> HistoricalEarningsData:
    """
    Calls Alpha Vantage APIs to fetch comprehensive historical earnings data for analysis.
    
    Args:
        symbol: Stock symbol to research
    Returns:
        HistoricalEarningsData containing quarterly earnings, annual earnings, and income statement data
    """
    try:
        # Get quarterly and annual earnings data
        raw_earnings: RawEarnings = call_alpha_vantage_earnings(symbol)
        
        # Get income statement data for margin analysis
        income_statement = call_alpha_vantage_income_statement(symbol)
        
        # Clean and prepare the data
        quarterly_earnings = raw_earnings.get('quarterlyEarnings', [])
        annual_earnings = raw_earnings.get('annualEarnings', [])
        income_statement_data = income_statement.get('annualReports', [])
        
        # For historical analysis, we want more data - take up to 20 quarters
        if quarterly_earnings:
            quarterly_earnings = quarterly_earnings[:10]
            
        # Take up to 10 years of annual data
        if annual_earnings:
            annual_earnings = annual_earnings[:5]
            
        # Take up to 10 years of income statement data
        if income_statement_data:
            income_statement_data = income_statement_data[:5]
        
        historical_data = HistoricalEarningsData(
            symbol=symbol,
            quarterly_earnings=quarterly_earnings,
            annual_earnings=annual_earnings,
            income_statement=income_statement_data
        )
        
        log.info(f"Successfully retrieved historical earnings data for {symbol}")
        return historical_data
        
    except Exception as e:
        log.error(f"Failed to get historical earnings data for symbol: {symbol}. Error: {e}")
        # Return empty data structure to allow graceful handling
        return HistoricalEarningsData(
            symbol=symbol,
            quarterly_earnings=[],
            annual_earnings=[],
            income_statement=[]
        )


def calculate_earnings_beat_miss_pattern(quarterly_earnings: list) -> Dict[str, Any]:
    """
    Calculate patterns in earnings beats and misses from quarterly data.
    
    Args:
        quarterly_earnings: List of quarterly earnings data from Alpha Vantage
    Returns:
        Dictionary containing beat/miss statistics and patterns
    """
    if not quarterly_earnings:
        return {
            "total_quarters": 0,
            "beats": 0,
            "misses": 0,
            "meets": 0,
            "beat_percentage": 0.0,
            "pattern": "INSUFFICIENT_DATA"
        }
    
    beats = 0
    misses = 0
    meets = 0
    valid_quarters = 0
    
    for quarter in quarterly_earnings:
        try:
            reported_eps = float(quarter.get('reportedEPS', 0))
            estimated_eps = float(quarter.get('estimatedEPS', 0))
            
            # Skip if either value is missing or zero (likely invalid data)
            if reported_eps == 0 or estimated_eps == 0:
                continue
                
            valid_quarters += 1
            
            if reported_eps > estimated_eps:
                beats += 1
            elif reported_eps < estimated_eps:
                misses += 1
            else:
                meets += 1
                
        except (ValueError, TypeError):
            continue
    
    if valid_quarters == 0:
        return {
            "total_quarters": 0,
            "beats": 0,
            "misses": 0,
            "meets": 0,
            "beat_percentage": 0.0,
            "pattern": "INSUFFICIENT_DATA"
        }
    
    beat_percentage = (beats / valid_quarters) * 100
    
    # Determine pattern
    if beat_percentage >= 80:
        pattern = "CONSISTENT_BEATS"
    elif beat_percentage <= 20:
        pattern = "CONSISTENT_MISSES"
    elif 40 <= beat_percentage <= 60:
        pattern = "MIXED_PATTERN"
    else:
        pattern = "VOLATILE"
    
    return {
        "total_quarters": valid_quarters,
        "beats": beats,
        "misses": misses,
        "meets": meets,
        "beat_percentage": beat_percentage,
        "pattern": pattern
    }


def calculate_revenue_growth_trend(annual_earnings: list) -> Dict[str, Any]:
    """
    Calculate revenue growth trends from annual earnings data.
    
    Args:
        annual_earnings: List of annual earnings data from Alpha Vantage
    Returns:
        Dictionary containing revenue growth statistics and trends
    """
    if not annual_earnings or len(annual_earnings) < 2:
        return {
            "years_analyzed": len(annual_earnings) if annual_earnings else 0,
            "growth_rates": [],
            "avg_growth_rate": 0.0,
            "trend": "INSUFFICIENT_DATA"
        }
    
    growth_rates = []
    
    # Calculate year-over-year revenue growth rates
    for i in range(len(annual_earnings) - 1):
        try:
            current_revenue = float(annual_earnings[i].get('totalRevenue', 0))
            previous_revenue = float(annual_earnings[i + 1].get('totalRevenue', 0))
            
            if previous_revenue == 0:
                continue
                
            growth_rate = ((current_revenue - previous_revenue) / previous_revenue) * 100
            growth_rates.append(growth_rate)
            
        except (ValueError, TypeError):
            continue
    
    if not growth_rates:
        return {
            "years_analyzed": 0,
            "growth_rates": [],
            "avg_growth_rate": 0.0,
            "trend": "INSUFFICIENT_DATA"
        }
    
    avg_growth_rate = sum(growth_rates) / len(growth_rates)
    
    # Determine trend by looking at the progression
    if len(growth_rates) >= 3:
        recent_avg = sum(growth_rates[:2]) / 2  # Most recent 2 years
        older_avg = sum(growth_rates[2:]) / len(growth_rates[2:])  # Older years
        
        if recent_avg > older_avg + 2:  # 2% threshold for acceleration
            trend = "ACCELERATING"
        elif recent_avg < older_avg - 2:  # 2% threshold for deceleration
            trend = "DECELERATING"
        elif avg_growth_rate < -5:
            trend = "DECLINING"
        elif max(growth_rates) - min(growth_rates) > 20:  # High variance
            trend = "VOLATILE"
        else:
            trend = "STABLE"
    else:
        # Limited data, use simple classification
        if avg_growth_rate < -5:
            trend = "DECLINING"
        elif max(growth_rates) - min(growth_rates) > 20:
            trend = "VOLATILE"
        else:
            trend = "STABLE"
    
    return {
        "years_analyzed": len(growth_rates),
        "growth_rates": growth_rates,
        "avg_growth_rate": avg_growth_rate,
        "trend": trend
    }


def calculate_margin_trend(income_statement: list) -> Dict[str, Any]:
    """
    Calculate margin trends from income statement data.
    
    Args:
        income_statement: List of annual income statement data from Alpha Vantage
    Returns:
        Dictionary containing margin statistics and trends
    """
    if not income_statement or len(income_statement) < 2:
        return {
            "years_analyzed": len(income_statement) if income_statement else 0,
            "gross_margins": [],
            "operating_margins": [],
            "net_margins": [],
            "trend": "INSUFFICIENT_DATA"
        }
    
    gross_margins = []
    operating_margins = []
    net_margins = []
    
    for year_data in income_statement:
        try:
            total_revenue = float(year_data.get('totalRevenue', 0))
            if total_revenue == 0:
                continue
                
            # Calculate gross margin
            gross_profit = float(year_data.get('grossProfit', 0))
            gross_margin = (gross_profit / total_revenue) * 100
            gross_margins.append(gross_margin)
            
            # Calculate operating margin
            operating_income = float(year_data.get('operatingIncome', 0))
            operating_margin = (operating_income / total_revenue) * 100
            operating_margins.append(operating_margin)
            
            # Calculate net margin
            net_income = float(year_data.get('netIncome', 0))
            net_margin = (net_income / total_revenue) * 100
            net_margins.append(net_margin)
            
        except (ValueError, TypeError, KeyError):
            continue
    
    if not gross_margins:
        return {
            "years_analyzed": 0,
            "gross_margins": [],
            "operating_margins": [],
            "net_margins": [],
            "trend": "INSUFFICIENT_DATA"
        }
    
    # Analyze trends (recent vs older periods)
    def analyze_margin_direction(margins):
        if len(margins) < 2:
            return "STABLE"
        
        if len(margins) >= 3:
            recent_avg = sum(margins[:2]) / 2
            older_avg = sum(margins[2:]) / len(margins[2:])
            
            if recent_avg > older_avg + 1:  # 1% threshold for improvement
                return "IMPROVING"
            elif recent_avg < older_avg - 1:  # 1% threshold for deterioration
                return "DETERIORATING"
            elif max(margins) - min(margins) > 10:  # High variance
                return "VOLATILE"
            else:
                return "STABLE"
        else:
            # Limited data
            if margins[0] > margins[1] + 1:
                return "IMPROVING"
            elif margins[0] < margins[1] - 1:
                return "DETERIORATING"
            else:
                return "STABLE"
    
    gross_trend = analyze_margin_direction(gross_margins)
    operating_trend = analyze_margin_direction(operating_margins)
    net_trend = analyze_margin_direction(net_margins)
    
    # Overall trend is the most concerning trend
    if any(trend == "DETERIORATING" for trend in [gross_trend, operating_trend, net_trend]):
        overall_trend = "DETERIORATING"
    elif any(trend == "VOLATILE" for trend in [gross_trend, operating_trend, net_trend]):
        overall_trend = "VOLATILE"
    elif any(trend == "IMPROVING" for trend in [gross_trend, operating_trend, net_trend]):
        overall_trend = "IMPROVING"
    else:
        overall_trend = "STABLE"
    
    return {
        "years_analyzed": len(gross_margins),
        "gross_margins": gross_margins,
        "operating_margins": operating_margins,
        "net_margins": net_margins,
        "gross_trend": gross_trend,
        "operating_trend": operating_trend,
        "net_trend": net_trend,
        "trend": overall_trend
    }