from legacy.research.news_sentiment.news_sentiment_util import get_news_sentiment_summary_for_peer_group
from legacy.research.news_sentiment.news_sentiment_models import RawNewsSentimentSummary
from typing import List
import logging

logger = logging.getLogger(__name__)

async def news_sentiment_fetch_summaries_task(
    symbol:str,
    peer_group: List[str],
) -> List[RawNewsSentimentSummary]:
    peer_group.append(symbol)
    logger.info(f"Fetching news sentiment summaries for peer group: {peer_group}")
    summaries = get_news_sentiment_summary_for_peer_group(peer_group)
    logger.debug(f"News sentiment summaries fetched for peer group: {peer_group}")
    return summaries
