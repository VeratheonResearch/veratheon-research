from legacy.research.news_sentiment.news_sentiment_models import NewsSentimentSummary, RawNewsSentimentSummary
from legacy.tasks.news_sentiment.news_sentiment_analysis_task import news_sentiment_analysis_task
from legacy.tasks.news_sentiment.news_sentiment_fetch_summaries_task import news_sentiment_fetch_summaries_task
from legacy.tasks.news_sentiment.news_sentiment_reporting_task import news_sentiment_reporting_task
from legacy.tasks.cache_retrieval.news_sentiment_cache_retrieval_task import news_sentiment_cache_retrieval_task
from legacy.research.common.models.peer_group import PeerGroup
from typing import List, Optional, Any
import logging
import time

logger = logging.getLogger(__name__)


async def news_sentiment_flow(
    symbol: str,
    peer_group: PeerGroup,
    earnings_projections_analysis: Optional[Any] = None,
    management_guidance_analysis: Optional[Any] = None,
    force_recompute: bool = False,
) -> NewsSentimentSummary:
    
    start_time = time.time()
    logger.info(f"News Sentiment flow started for {symbol}")
    
    # Try to get cached report first
    cached_result = await news_sentiment_cache_retrieval_task(symbol, peer_group, earnings_projections_analysis, management_guidance_analysis, force_recompute)
    if cached_result is not None:
        logger.info(f"Returning cached news sentiment analysis for {symbol}")
        return cached_result
    
    logger.info(f"No cached data found, running fresh news sentiment analysis for {symbol}")

    peer_group_summaries: List[RawNewsSentimentSummary] = await news_sentiment_fetch_summaries_task(symbol, peer_group.peer_group)

    news_sentiment_analysis_task_result: NewsSentimentSummary = await news_sentiment_analysis_task(
        symbol, peer_group_summaries, earnings_projections_analysis, management_guidance_analysis
    )

    # Generate reporting output
    await news_sentiment_reporting_task(symbol, news_sentiment_analysis_task_result)

    logger.info(f"News Sentiment flow completed for {symbol} in {int(time.time() - start_time)} seconds")
    

    return news_sentiment_analysis_task_result
