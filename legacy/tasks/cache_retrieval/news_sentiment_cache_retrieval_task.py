from src.lib.supabase_cache import get_supabase_cache
from legacy.research.news_sentiment.news_sentiment_models import NewsSentimentSummary
from legacy.research.common.models.peer_group import PeerGroup
from legacy.research.earnings_projections.earnings_projections_models import EarningsProjectionAnalysis
from legacy.research.management_guidance.management_guidance_models import ManagementGuidanceAnalysis
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def news_sentiment_cache_retrieval_task(
    symbol: str, 
    peer_group: PeerGroup,
    earnings_projections_analysis: EarningsProjectionAnalysis,
    management_guidance_analysis: ManagementGuidanceAnalysis,
    force_recompute: bool = False
) -> Optional[NewsSentimentSummary]:
    """
    Cache retrieval task for news sentiment analysis.
    
    Checks Redis cache for existing news sentiment report. If found, returns cached data.
    If not found, returns None. If force_recompute is True, skips cache lookup.
    
    Args:
        symbol: Stock symbol to analyze
        peer_group: Peer group analysis context
        earnings_projections_analysis: Earnings projections analysis context
        management_guidance_analysis: Management guidance analysis context
        force_recompute: If True, skip cache lookup and return None
        
    Returns:
        NewsSentimentSummary from cache or None if cache miss/force_recompute
    """
    if force_recompute:
        logger.info(f"Skipping cache lookup for news sentiment analysis: {symbol} (force_recompute=True)")
        return None
        
    logger.info(f"Checking cache for news sentiment analysis: {symbol}")
    
    cache = get_supabase_cache()
    cached_report = cache.get_cached_report("news_sentiment", symbol)
    
    if cached_report:
        logger.info(f"Cache hit for news sentiment analysis: {symbol}")
        # Remove cache metadata for clean model reconstruction
        clean_data = {k: v for k, v in cached_report.items() if not k.startswith('_cache_')}
        try:
            return NewsSentimentSummary(**clean_data)
        except Exception as e:
            logger.warning(f"Failed to reconstruct cached data for {symbol}, falling back to fresh analysis: {str(e)}")
    else:
        logger.info(f"Cache miss for news sentiment analysis: {symbol}")
    
    # Cache miss or reconstruction failed
    return None