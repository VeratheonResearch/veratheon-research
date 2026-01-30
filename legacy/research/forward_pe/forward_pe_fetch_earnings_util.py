from typing import List, Dict, Any
from src.lib.alpha_vantage_api import call_alpha_vantage_earnings, call_alpha_vantage_earnings_estimates, call_alpha_vantage_global_quote, call_alpha_vantage_overview
from src.lib.fiscal_year_utils import log_fiscal_decision
from legacy.research.forward_pe.forward_pe_models import ForwardPEEarningsSummary
from legacy.research.common.models.earnings import RawEarnings, RawGlobalQuote

import logging
log = logging.getLogger(__name__)

def get_quarterly_eps_data_for_symbol(symbol: str) -> ForwardPEEarningsSummary:
    """
    Calls Alpha Vantage APIs for the specified symbol and returns all necessary data for forward PE analysis.
    Uses fiscal year timing to ensure consensus EPS alignment with analysis timeframe.

    Args:
        symbol: Stock symbol to research
    Returns:
        ForwardPEEarningsSummary containing the earnings data
    """
    # Get fiscal year timing for proper data alignment
    fiscal_info = log_fiscal_decision(symbol)

    raw_earnings: RawEarnings = call_alpha_vantage_earnings(symbol)
    raw_global_quote: RawGlobalQuote = call_alpha_vantage_global_quote(symbol)
    current_price = raw_global_quote['Global Quote']['05. price']
    overview = call_alpha_vantage_overview(symbol)
    clean_overview_of_useless_data(overview)

    # Adjust quarters based on fiscal timing
    if fiscal_info.use_annual_data:
        # Near fiscal year end - focus on annual consistency
        quarters = 4  # Last 4 quarters for annual view
        log.info(f"Using annual-focused earnings data for {symbol} (near fiscal year end)")
    else:
        # Mid-year - use more quarterly data for trends
        quarters = 9  # More quarters for trend analysis
        log.info(f"Using quarterly-focused earnings data for {symbol} (mid fiscal year)")

    if raw_earnings['quarterlyEarnings']:
        raw_earnings['quarterlyEarnings'] = raw_earnings['quarterlyEarnings'][:quarters]

    # Get consensus EPS estimate using the Earnings Estimates API
    estimates_json = call_alpha_vantage_earnings_estimates(symbol)
    next_quarter_consensus_eps = extract_next_quarter_eps_from_estimates(estimates_json)

    earnings_summary = ForwardPEEarningsSummary(
        symbol=symbol,
        overview=overview,
        quarterly_earnings=raw_earnings['quarterlyEarnings'],
        consensus_eps_next_quarter=str(next_quarter_consensus_eps),
        current_price=current_price
    )

    return earnings_summary


def extract_next_quarter_eps_from_estimates(estimates_json: Dict[str, Any]) -> str:
    """
    Extract the next quarter's consensus EPS estimate from the Earnings Estimates API response.

    Args:
        estimates_json: Response from call_alpha_vantage_earnings_estimates
    Returns:
        Next quarter's consensus EPS estimate as string, or fallback message
    """
    try:
        estimates = estimates_json.get('estimates', [])
        if estimates:
            # Look for the next fiscal quarter estimate
            for estimate in estimates:
                if estimate.get('horizon') == 'next fiscal quarter':
                    return str(estimate.get('eps_estimate_average', "Not enough consensus"))
            # Fallback to first estimate if no specific next quarter found
            return str(estimates[0].get('eps_estimate_average', "Not enough consensus"))
        return "Not enough consensus"
    except Exception as e:
        log.warning(f"Error extracting EPS from estimates: {e}")
        return "Not enough consensus"




def get_quarterly_eps_data_for_symbols(symbols: List[str]) -> List[ForwardPEEarningsSummary]:
    """
    Calls Alpha Vantage APIs for the specified symbols and returns all necessary data for forward PE analysis.
    Uses Earnings Estimates API for consensus EPS data.

    Args:
        symbols: List of stock symbols to get earnings for

    Returns:
        A list of ForwardPEEarningsSummary objects containing annual and quarterly earnings data,
        as well as the next quarter's consensus EPS estimate, and the latest closing price.
    """
    earnings_summaries = []

    for symbol in symbols:
        try:
            # Get the overview data for the symbol
            overview_json = call_alpha_vantage_overview(symbol)
            # If the overview data is empty, skip this symbol
            if not overview_json:
                log.warning(f"Overview data is empty for symbol: {symbol}. Skipping.")
                continue

            # Get the earnings data for the symbol
            raw_earnings: RawEarnings = call_alpha_vantage_earnings(symbol)

            # Get consensus EPS estimate using the Earnings Estimates API
            estimates_json = call_alpha_vantage_earnings_estimates(symbol)
            next_quarter_consensus_eps = extract_next_quarter_eps_from_estimates(estimates_json)

            raw_global_quote: RawGlobalQuote = call_alpha_vantage_global_quote(symbol)
            current_price = raw_global_quote['Global Quote']['05. price']

            overview = call_alpha_vantage_overview(symbol)
            clean_overview_of_useless_data(overview)

            # Truncate quarterly earnings first
            # Always return 9 quarters of data
            quarters = 9
            if raw_earnings['quarterlyEarnings']:
                raw_earnings['quarterlyEarnings'] = raw_earnings['quarterlyEarnings'][:quarters]

            earnings_summary = ForwardPEEarningsSummary(
                symbol=symbol,
                overview=overview,
                quarterly_earnings=raw_earnings['quarterlyEarnings'],
                consensus_eps_next_quarter=str(next_quarter_consensus_eps),
                current_price=current_price
            )

            earnings_summaries.append(earnings_summary)

        except Exception as e:
            log.warning(f"Failed to get earnings data for symbol: {symbol}. Error: {e}. Skipping.")
            continue

    return earnings_summaries


def clean_earnings_of_useless_data(earnings: Dict[str, Any]) -> Dict[str, Any]:
    # Remove dates that dont matter
    earnings.pop()

def clean_overview_of_useless_data(overview: Dict[str, Any]) -> Dict[str, Any]:
    # Remove the Description, address, and other useless data
    overview.pop("Symbol", None)
    overview.pop("AssetType", None)
    overview.pop("Name", None)
    overview.pop("Description", None)
    overview.pop("CIK", None)
    overview.pop("Exchange", None)
    overview.pop("Currency", None)
    overview.pop("Country", None)
    overview.pop("Sector", None)
    overview.pop("Industry", None)
    overview.pop("Address", None)
    overview.pop("OfficialSite", None)
    overview.pop("FiscalYearEnd", None)
    overview.pop("LatestQuarter", None)
    # overview.pop("MarketCapitalization", None)
    # overview.pop("Beta", None)
    # overview.pop("52WeekHigh", None)
    # overview.pop("52WeekLow", None)
    # overview.pop("50DayMovingAverage", None)
    # overview.pop("200DayMovingAverage", None)
    # overview.pop("SharesOutstanding", None)
    overview.pop("SharesFloat", None)
    overview.pop("PercentInsiders", None)
    overview.pop("PercentInstitutions", None)
    overview.pop("DividendDate", None)
    overview.pop("ExDividendDate", None)
    overview.pop("AnalystRatingStrongBuy", None)
    overview.pop("AnalystRatingBuy", None)
    overview.pop("AnalystRatingHold", None)
    overview.pop("AnalystRatingSell", None)
    overview.pop("AnalystRatingStrongSell", None)
    # overview.pop("AnalystTargetPrice", None)
    

    
    
    
    