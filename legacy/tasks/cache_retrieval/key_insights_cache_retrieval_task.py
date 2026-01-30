from src.lib.supabase_cache import get_supabase_cache
from legacy.research.comprehensive_report.comprehensive_report_models import KeyInsights, ComprehensiveReport
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def key_insights_cache_retrieval_task(
    symbol: str,
    comprehensive_report: ComprehensiveReport,
    force_recompute: bool = False
) -> Optional[KeyInsights]:
    """
    Cache retrieval task for key insights analysis.
    
    Checks Redis cache for existing key insights. If found, returns cached data.
    If not found, returns None. If force_recompute is True, skips cache lookup.
    
    Args:
        symbol: Stock symbol
        comprehensive_report: The comprehensive report used as input
        force_recompute: If True, bypass cache
        
    Returns:
        KeyInsights from cache or None if cache miss/force_recompute
    """
    if force_recompute:
        logger.info(f"Skipping cache lookup for key insights: {symbol} (force_recompute=True)")
        return None
        
    logger.info(f"Checking cache for key insights: {symbol}")
    
    cache = get_supabase_cache()
    cached_insights = cache.get_cached_report("key_insights", symbol)
    
    if cached_insights:
        logger.info(f"Cache hit for key insights: {symbol}")
        # Remove cache metadata for clean model reconstruction
        clean_data = {k: v for k, v in cached_insights.items() if not k.startswith('_cache_')}
        try:
            return KeyInsights(**clean_data)
        except Exception as e:
            logger.warning(f"Failed to reconstruct cached key insights for {symbol}, falling back to fresh analysis: {str(e)}")
    else:
        logger.info(f"Cache miss for key insights: {symbol}")
    
    # Cache miss or reconstruction failed
    return None