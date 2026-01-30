import logging
import time
from legacy.tasks.comprehensive_report.key_insights_task import key_insights_task
from legacy.tasks.comprehensive_report.key_insights_reporting_task import key_insights_reporting_task
from legacy.tasks.cache_retrieval.key_insights_cache_retrieval_task import key_insights_cache_retrieval_task
from legacy.research.comprehensive_report.comprehensive_report_models import KeyInsights, ComprehensiveReport

logger = logging.getLogger(__name__)


async def key_insights_flow(
    symbol: str,
    comprehensive_report: ComprehensiveReport,
    force_recompute: bool = False
) -> KeyInsights:
    """
    Generate key insights from comprehensive report.
    This subflow extracts the most critical investment insights from the detailed technical report.
    
    Args:
        symbol: Stock symbol
        comprehensive_report: The comprehensive technical report
        force_recompute: Whether to bypass cache and regenerate
        
    Returns:
        KeyInsights: Critical investment insights for decision-making
    """
    
    start_time = time.time()
    logger.info(f"Key insights flow started for {symbol}")
    
    # Try to get cached insights first
    cached_result = await key_insights_cache_retrieval_task(symbol, comprehensive_report, force_recompute)
    if cached_result is not None:
        logger.info(f"Returning cached key insights for {symbol}")
        return cached_result
    
    logger.info(f"No cached data found, running fresh key insights analysis for {symbol}")
    
    key_insights = await key_insights_task(symbol, comprehensive_report)
    
    # Generate reporting output
    await key_insights_reporting_task(symbol, key_insights)
    
    logger.info(f"Key insights flow completed for {symbol} in {int(time.time() - start_time)} seconds")
    
    return key_insights