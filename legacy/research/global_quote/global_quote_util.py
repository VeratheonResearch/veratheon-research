import logging
from src.lib.alpha_vantage_api import call_alpha_vantage_global_quote
from legacy.research.global_quote.global_quote_models import GlobalQuoteData

log = logging.getLogger(__name__)


def get_global_quote_data_for_symbol(symbol: str) -> GlobalQuoteData:
    """
    Calls Alpha Vantage API to fetch current price data.
    
    Args:
        symbol: Stock symbol to research
    Returns:
        GlobalQuoteData containing current price
    """
    try:
        # Get global quote data from Alpha Vantage
        quote_data = call_alpha_vantage_global_quote(symbol)
        
        # Extract the quote information (Alpha Vantage returns it under "Global Quote" key)
        global_quote = quote_data.get("Global Quote", {})
        
        # Create GlobalQuoteData object with only the price
        quote = GlobalQuoteData(
            symbol=global_quote.get("01. symbol", symbol),
            price=global_quote.get("05. price")
        )
        
        log.info(f"Successfully retrieved global quote data for {symbol}")
        return quote
        
    except Exception as e:
        log.error(f"Failed to get global quote data for symbol: {symbol}. Error: {e}")
        # Return minimal data structure to allow graceful handling
        return GlobalQuoteData(
            symbol=symbol
        )