from src.lib.supabase_cache import get_supabase_cache
from legacy.research.cross_reference.cross_reference_models import CrossReferencedAnalysisCompletion
from legacy.research.forward_pe.forward_pe_models import ForwardPeValuation
from legacy.research.news_sentiment.news_sentiment_models import NewsSentimentSummary
from legacy.research.historical_earnings.historical_earnings_models import HistoricalEarningsAnalysis
from legacy.research.financial_statements.financial_statements_models import FinancialStatementsAnalysis
from legacy.research.earnings_projections.earnings_projections_models import EarningsProjectionAnalysis
from legacy.research.management_guidance.management_guidance_models import ManagementGuidanceAnalysis
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

async def cross_reference_cache_retrieval_task(
    symbol: str, 
    forward_pe_valuation: ForwardPeValuation,
    news_sentiment_summary: NewsSentimentSummary,
    historical_earnings_analysis: HistoricalEarningsAnalysis,
    financial_statements_analysis: FinancialStatementsAnalysis,
    earnings_projections_analysis: EarningsProjectionAnalysis,
    management_guidance_analysis: ManagementGuidanceAnalysis,
    force_recompute: bool = False
) -> Optional[List[CrossReferencedAnalysisCompletion]]:
    """
    Cache retrieval task for cross reference analysis.
    
    Checks Redis cache for existing cross reference report. If found, returns cached data.
    If not found, returns None. If force_recompute is True, skips cache lookup.
    
    Args:
        symbol: Stock symbol to analyze
        forward_pe_valuation: Forward PE valuation analysis context
        news_sentiment_summary: News sentiment analysis context
        historical_earnings_analysis: Historical earnings analysis context
        financial_statements_analysis: Financial statements analysis context
        earnings_projections_analysis: Earnings projections analysis context
        management_guidance_analysis: Management guidance analysis context
        force_recompute: If True, skip cache lookup and return None
        
    Returns:
        List[CrossReferencedAnalysisCompletion] from cache or None if cache miss/force_recompute
    """
    if force_recompute:
        logger.info(f"Skipping cache lookup for cross reference analysis: {symbol} (force_recompute=True)")
        return None
        
    logger.info(f"Checking cache for cross reference analysis: {symbol}")
    
    cache = get_supabase_cache()
    cached_report = cache.get_cached_report("cross_reference", symbol)
    
    if cached_report:
        logger.info(f"Cache hit for cross reference analysis: {symbol}")
        # Remove cache metadata for clean model reconstruction
        clean_data = {k: v for k, v in cached_report.items() if not k.startswith('_cache_')}
        try:
            # For cross reference, the cached data should be a list of dicts
            if isinstance(clean_data.get('data'), list):
                return [CrossReferencedAnalysisCompletion(**item) for item in clean_data['data']]
            else:
                # Handle the case where data was stored directly as list
                return [CrossReferencedAnalysisCompletion(**item) for item in clean_data]
        except Exception as e:
            logger.warning(f"Failed to reconstruct cached data for {symbol}, falling back to fresh analysis: {str(e)}")
    else:
        logger.info(f"Cache miss for cross reference analysis: {symbol}")
    
    # Cache miss or reconstruction failed
    return None