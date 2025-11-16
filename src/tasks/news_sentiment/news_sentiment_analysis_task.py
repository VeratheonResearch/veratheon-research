from src.research.news_sentiment.news_sentiment_agent import news_sentiment_agent
from src.research.news_sentiment.news_sentiment_models import RawNewsSentimentSummary, NewsSentimentSummary
from agents import Runner
from src.lib.token_logger_hook import TokenLoggerHook
from typing import List, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

async def news_sentiment_analysis_task(
    symbol: str,
    raw_news_sentiment_summaries: List[RawNewsSentimentSummary],
    earnings_projections_analysis: Optional[Any] = None,
    management_guidance_analysis: Optional[Any] = None,
) -> NewsSentimentSummary:
    logger.info(f"Performing news sentiment analysis for {symbol}")
    # Build input with optional context
    input_data = f"symbol: {symbol}, raw_news_sentiment_summaries: {raw_news_sentiment_summaries}"
    if earnings_projections_analysis:
        input_data += f", earnings_projections_analysis: {earnings_projections_analysis}"
    if management_guidance_analysis:
        input_data += f", management_guidance_analysis: {management_guidance_analysis}"
    
    result = await Runner.run(news_sentiment_agent, input=input_data, hooks=TokenLoggerHook(symbol=symbol))
    logger.info(f"News sentiment analysis completed for {symbol}")
    logger.debug(f"News sentiment analysis for {symbol}: {json.dumps(result.final_output.model_dump(), indent=2)}")
    return result.final_output
    