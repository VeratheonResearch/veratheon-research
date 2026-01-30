from src.lib.supabase_cache import get_supabase_cache
from legacy.research.earnings_projections.earnings_projections_models import EarningsProjectionAnalysis
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

async def earnings_projections_cache_retrieval_task(
    symbol: str, 
    historical_earnings_context: Dict[str, Any], 
    financial_statements_context: Dict[str, Any],
    force_recompute: bool = False
) -> Optional[EarningsProjectionAnalysis]:
    """
    Cache retrieval task for earnings projections analysis.
    
    Checks Redis cache for existing earnings projections report. If found, returns cached data.
    If not found, returns None. If force_recompute is True, skips cache lookup.
    
    Args:
        symbol: Stock symbol to analyze
        historical_earnings_context: Historical earnings analysis context
        financial_statements_context: Financial statements analysis context
        force_recompute: If True, skip cache lookup and return None
        
    Returns:
        EarningsProjectionAnalysis from cache or None if cache miss/force_recompute
    """
    if force_recompute:
        logger.info(f"Skipping cache lookup for earnings projections analysis: {symbol} (force_recompute=True)")
        return None
        
    logger.info(f"Checking cache for earnings projections analysis: {symbol}")
    
    cache = get_supabase_cache()
    cached_report = cache.get_cached_report("earnings_projections", symbol)
    
    if cached_report:
        logger.info(f"Cache hit for earnings projections analysis: {symbol}")
        # Remove cache metadata for clean model reconstruction
        clean_data = {k: v for k, v in cached_report.items() if not k.startswith('_cache_')}
        try:
            return EarningsProjectionAnalysis(**clean_data)
        except Exception as e:
            logger.warning(f"Failed to reconstruct cached data for {symbol}, falling back to fresh analysis: {str(e)}")
    else:
        logger.info(f"Cache miss for earnings projections analysis: {symbol}")
    
    # Cache miss or reconstruction failed
    return None