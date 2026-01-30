from legacy.tasks.global_quote.global_quote_fetch_task import global_quote_fetch_task
from legacy.tasks.global_quote.global_quote_reporting_task import global_quote_reporting_task
from legacy.tasks.cache_retrieval.global_quote_cache_retrieval_task import global_quote_cache_retrieval_task
from legacy.research.global_quote.global_quote_models import GlobalQuoteData
import logging
import time

logger = logging.getLogger(__name__)

async def global_quote_flow(symbol: str, force_recompute: bool = False) -> GlobalQuoteData:
    """
    Main flow for fetching global quote data.
    
    Fetches current price from Alpha Vantage Global Quote API.
    
    Args:
        symbol: Stock symbol to research
        force_recompute: If True, skip cache and recompute data
    Returns:
        GlobalQuoteData containing current price
    """
    
    start_time = time.time()
    logger.info(f"Global Quote flow started for {symbol}")
    
    # Try to get cached data first
    cached_result = await global_quote_cache_retrieval_task(symbol, force_recompute)
    if cached_result is not None:
        logger.info(f"Returning cached global quote data for {symbol}")
        return cached_result
    
    logger.info(f"No cached data found, fetching fresh global quote data for {symbol}")
    
    # Fetch global quote data from Alpha Vantage
    quote_data: GlobalQuoteData = await global_quote_fetch_task(symbol)

    # Generate reporting output
    await global_quote_reporting_task(symbol, quote_data)

    logger.info(f"Global Quote flow completed for {symbol} in {int(time.time() - start_time)} seconds")
    

    return quote_data