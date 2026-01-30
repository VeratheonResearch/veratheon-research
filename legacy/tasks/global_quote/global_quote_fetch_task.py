from legacy.research.global_quote.global_quote_models import GlobalQuoteData
from legacy.research.global_quote.global_quote_util import get_global_quote_data_for_symbol
import logging
import json

logger = logging.getLogger(__name__)

async def global_quote_fetch_task(symbol: str) -> GlobalQuoteData:
    """
    Task to fetch global quote data from Alpha Vantage.
    
    Args:
        symbol: Stock symbol to research
    Returns:
        GlobalQuoteData containing current price
    """
    logger.info(f"Fetching global quote data for {symbol}")

    quote_data = get_global_quote_data_for_symbol(symbol)
    
    logger.info(f"Global quote data fetched for {symbol}: price ${quote_data.price}")

    logger.debug(f"Global quote data fetched for {symbol}: {json.dumps(quote_data.model_dump(), indent=2)}")

    return quote_data