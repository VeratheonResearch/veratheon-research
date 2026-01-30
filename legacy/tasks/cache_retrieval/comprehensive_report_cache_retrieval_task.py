from src.lib.supabase_cache import get_supabase_cache
from legacy.research.comprehensive_report.comprehensive_report_models import ComprehensiveReport
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

async def comprehensive_report_cache_retrieval_task(
    symbol: str,
    all_analyses: Dict[str, Any],
    force_recompute: bool = False
) -> Optional[ComprehensiveReport]:
    """
    Cache retrieval task for comprehensive report analysis.
    
    Checks Redis cache for existing comprehensive report. If found, returns cached data.
    If not found, returns None. If force_recompute is True, skips cache lookup.
    
    Args:
        symbol: Stock symbol to analyze
        all_analyses: All analysis results (used for cache key generation context)
        force_recompute: If True, skip cache lookup and return None
        
    Returns:
        ComprehensiveReport from cache or None if cache miss/force_recompute
    """
    if force_recompute:
        logger.info(f"Skipping cache lookup for comprehensive report: {symbol} (force_recompute=True)")
        return None
        
    logger.info(f"Checking cache for comprehensive report: {symbol}")
    
    cache = get_supabase_cache()
    cached_report = cache.get_cached_report("comprehensive_report", symbol)
    
    if cached_report:
        logger.info(f"Cache hit for comprehensive report: {symbol}")
        # Remove cache metadata for clean model reconstruction
        clean_data = {k: v for k, v in cached_report.items() if not k.startswith('_cache_')}
        try:
            return ComprehensiveReport(**clean_data)
        except Exception as e:
            logger.warning(f"Failed to reconstruct cached comprehensive report for {symbol}, falling back to fresh analysis: {str(e)}")
    else:
        logger.info(f"Cache miss for comprehensive report: {symbol}")
    
    # Cache miss or reconstruction failed
    return None