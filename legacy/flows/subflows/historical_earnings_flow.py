from legacy.tasks.historical_earnings.historical_earnings_fetch_task import historical_earnings_fetch_task
from legacy.tasks.historical_earnings.historical_earnings_analysis_task import historical_earnings_analysis_task
from legacy.tasks.historical_earnings.historical_earnings_reporting_task import historical_earnings_reporting_task
from legacy.tasks.cache_retrieval.historical_earnings_cache_retrieval_task import historical_earnings_cache_retrieval_task
from legacy.research.historical_earnings.historical_earnings_models import HistoricalEarningsData, HistoricalEarningsAnalysis
import logging
import time

logger = logging.getLogger(__name__)

async def historical_earnings_flow(symbol: str, force_recompute: bool = False) -> HistoricalEarningsAnalysis:
    """
    Main flow for running historical earnings analysis.
    
    Analyzes historical earnings data for patterns in beats/misses, revenue growth rates, 
    and margin trends to establish baseline performance and predictability context.
    
    Args:
        symbol: Stock symbol to research
    Returns:
        HistoricalEarningsAnalysis containing the research results and patterns
    """
    
    start_time = time.time()
    logger.info(f"Historical Earnings flow started for {symbol}")
    
    # Try to get cached report first
    cached_result = await historical_earnings_cache_retrieval_task(symbol, force_recompute)
    if cached_result is not None:
        logger.info(f"Returning cached historical earnings analysis for {symbol}")
        return cached_result
    
    logger.info(f"No cached data found, running fresh historical earnings analysis for {symbol}")
    
    # Fetch historical earnings data from Alpha Vantage
    historical_data: HistoricalEarningsData = await historical_earnings_fetch_task(symbol)

    # Perform historical earnings analysis
    historical_analysis: HistoricalEarningsAnalysis = await historical_earnings_analysis_task(
        symbol, historical_data
    )

    # Generate reporting output
    await historical_earnings_reporting_task(symbol, historical_analysis)

    logger.info(f"Historical Earnings flow completed for {symbol} in {int(time.time() - start_time)} seconds")
    

    return historical_analysis  