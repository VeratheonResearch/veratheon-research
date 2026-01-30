from typing import List, Dict, Any
from src.lib.alpha_vantage_api import call_alpha_vantage_news_sentiment
from legacy.research.news_sentiment.news_sentiment_models import RawNewsSentimentSummary
import logging

logger = logging.getLogger(__name__)

def get_news_sentiment_summary_for_peer_group(peer_group: List[str]) -> List[RawNewsSentimentSummary]:
    news_sentiment_summaries = []
    for peer in peer_group:
        news_sentiment_dict = call_alpha_vantage_news_sentiment(tickers=peer)
        if "feed" not in news_sentiment_dict:
            logger.warning(f"No news sentiment data found for {peer}. Skipping.")
            continue
        clean_news_sentiment_dict = clean_news_sentiment_of_useless_data(news_sentiment_dict)
        news_sentiment_summary = RawNewsSentimentSummary(symbol=peer, **clean_news_sentiment_dict)
        news_sentiment_summaries.append(news_sentiment_summary)
    return news_sentiment_summaries
        
def clean_news_sentiment_of_useless_data(news_sentiment_dict: Dict[str, Any]) -> Dict[str, Any]:
    news_sentiment_dict.pop("items", None)
    news_sentiment_dict.pop("sentiment_score_definition", None)
    news_sentiment_dict.pop("relevance_score_definition", None)
    for news_item in news_sentiment_dict["feed"]:
            news_item.pop("title", None)
            news_item.pop("url", None)
            news_item.pop("time_published", None)
            news_item.pop("authors", None)
            news_item.pop("summary", None)
            news_item.pop("banner_image", None)
            news_item.pop("source", None)
            news_item.pop("category_within_source", None)
            news_item.pop("source_domain", None)
            news_item.pop("topics", None)
    return news_sentiment_dict