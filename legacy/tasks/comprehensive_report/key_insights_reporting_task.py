from src.lib.supabase_cache import get_supabase_cache
from legacy.research.comprehensive_report.comprehensive_report_models import KeyInsights
import logging

logger = logging.getLogger(__name__)

async def key_insights_reporting_task(symbol: str, key_insights: KeyInsights) -> None:
    """
    Reporting task for key insights analysis.
    
    Caches the key insights results to Redis for future retrieval.
    
    Args:
        symbol: Stock symbol analyzed
        key_insights: KeyInsights model with analysis results
    """
    logger.info(f"Caching key insights results for {symbol}")
    
    cache = get_supabase_cache()
    success = cache.cache_report(
        "key_insights", 
        symbol, 
        key_insights,
        ttl=24*60*60  # 24 hours
    )
    
    if success:
        logger.info(f"Successfully cached key insights for {symbol}")
    else:
        logger.warning(f"Failed to cache key insights for {symbol}")
        
    # Note: We don't raise exceptions here because caching failure 
    # shouldn't break the analysis flow