from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import enum


class SentimentTrend(str, enum.Enum):
    IMPROVING = "IMPROVING"
    DETERIORATING = "DETERIORATING"
    STABLE_POSITIVE = "STABLE_POSITIVE"
    STABLE_NEGATIVE = "STABLE_NEGATIVE"
    VOLATILE = "VOLATILE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class SentimentConfidence(str, enum.Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class NewsVolume(str, enum.Enum):
    HIGH_VOLUME = "HIGH_VOLUME"
    MODERATE_VOLUME = "MODERATE_VOLUME"
    LOW_VOLUME = "LOW_VOLUME"
    SPARSE_COVERAGE = "SPARSE_COVERAGE"

class RawNewsSentimentFeed(BaseModel):
    # title: str
    # url: str
    # time_published: str
    # authors: List[str]
    # summary: str
    # banner_image: Optional[str]
    # source: str
    # category_within_source: str
    # source_domain: str
    # topics: List[Dict[str, Any]]
    overall_sentiment_score: float
    overall_sentiment_label: str
    ticker_sentiment: List[Dict[str, Any]]

class RawNewsSentimentSummary(BaseModel):
    # items: int
    # sentiment_score_definition: str
    # relevance_score_definition: str
    feed: List[RawNewsSentimentFeed]
    

class NewsSentimentSummary(BaseModel):
    symbol: Optional[str]
    sentiment_trend: SentimentTrend
    news_volume: NewsVolume
    sentiment_confidence: SentimentConfidence
    key_themes: List[str]
    positive_catalysts: List[str]
    negative_concerns: List[str]
    news_sentiment_analysis: str
    long_form_analysis: str
    overall_sentiment_label: str
    critical_insights: str