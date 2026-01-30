from src.lib.supabase_cache import get_supabase_cache
from legacy.research.trade_ideas.trade_idea_models import TradeIdea
from legacy.research.forward_pe.forward_pe_models import ForwardPeValuation
from legacy.research.news_sentiment.news_sentiment_models import NewsSentimentSummary
from legacy.research.historical_earnings.historical_earnings_models import HistoricalEarningsAnalysis
from legacy.research.financial_statements.financial_statements_models import FinancialStatementsAnalysis
from legacy.research.earnings_projections.earnings_projections_models import EarningsProjectionAnalysis
from legacy.research.management_guidance.management_guidance_models import ManagementGuidanceAnalysis
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def trade_ideas_cache_retrieval_task(
    symbol: str, 
    forward_pe_valuation: ForwardPeValuation,
    news_sentiment_summary: NewsSentimentSummary,
    historical_earnings_analysis: HistoricalEarningsAnalysis,
    financial_statements_analysis: FinancialStatementsAnalysis,
    earnings_projections_analysis: EarningsProjectionAnalysis,
    management_guidance_analysis: ManagementGuidanceAnalysis,
    force_recompute: bool = False
) -> Optional[TradeIdea]:
    """
    Cache retrieval task for trade ideas analysis.
    
    Checks Redis cache for existing trade ideas report. If found, returns cached data.
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
        TradeIdea from cache or None if cache miss/force_recompute
    """
    if force_recompute:
        logger.info(f"Skipping cache lookup for trade ideas analysis: {symbol} (force_recompute=True)")
        return None
        
    logger.info(f"Checking cache for trade ideas analysis: {symbol}")
    
    cache = get_supabase_cache()
    cached_report = cache.get_cached_report("trade_ideas", symbol)
    
    if cached_report:
        logger.info(f"Cache hit for trade ideas analysis: {symbol}")
        # Remove cache metadata for clean model reconstruction
        clean_data = {k: v for k, v in cached_report.items() if not k.startswith('_cache_')}
        try:
            return TradeIdea(**clean_data)
        except Exception as e:
            logger.warning(f"Failed to reconstruct cached data for {symbol}, falling back to fresh analysis: {str(e)}")
    else:
        logger.info(f"Cache miss for trade ideas analysis: {symbol}")
    
    # Cache miss or reconstruction failed
    return None