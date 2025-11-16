import json
from src.research.forward_pe.forward_pe_models import ForwardPeValuation
from agents import Runner, RunResult
from src.lib.token_logger_hook import TokenLoggerHook
from src.research.trade_ideas.trade_idea_agent import trade_idea_agent
from src.research.trade_ideas.trade_idea_models import TradeIdea
from src.research.news_sentiment.news_sentiment_models import NewsSentimentSummary
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

async def trade_ideas_task(
    symbol: str,
    earnings_analysis: ForwardPeValuation,
    news_sentiment_summary: NewsSentimentSummary,
    historical_earnings_analysis: Optional[Any] = None,
    financial_statements_analysis: Optional[Any] = None,
    earnings_projections_analysis: Optional[Any] = None,
    management_guidance_analysis: Optional[Any] = None,
) -> TradeIdea:
    """
    Task to perform trade ideas for the forward PE research for a given symbol.

    Args:
        symbol: Stock symbol to research
        earnings_analysis: ForwardPeValuation containing the forward PE analysis
        news_sentiment_summary: NewsSentimentSummary containing the news sentiment summary
        historical_earnings_analysis: Optional historical earnings patterns for context
        financial_statements_analysis: Optional financial statements trends for context
        earnings_projections_analysis: Optional independent earnings projections for validation
        management_guidance_analysis: Optional management guidance insights for context
    Returns:
        TradeIdea containing the trade ideas for users with no position
    """
    logger.info(f"Performing trade ideas for users with no position in {symbol}")

    # Build comprehensive input with all available analyses
    input_data = f"original_symbol: {symbol}, earnings_analysis: {earnings_analysis}, news_sentiment_summary: {news_sentiment_summary}"
    
    if historical_earnings_analysis:
        input_data += f", historical_earnings_analysis: {historical_earnings_analysis}"
    if financial_statements_analysis:
        input_data += f", financial_statements_analysis: {financial_statements_analysis}"
    if earnings_projections_analysis:
        input_data += f", earnings_projections_analysis: {earnings_projections_analysis}"
    if management_guidance_analysis:
        input_data += f", management_guidance_analysis: {management_guidance_analysis}"

    result: RunResult = await Runner.run(
        trade_idea_agent,
        input=input_data,
        hooks=TokenLoggerHook(symbol=symbol)
    )
    trade_idea: TradeIdea = result.final_output

    logger.info(f"Trade idea for {symbol}: {json.dumps(trade_idea.model_dump(), indent=2)}")

    return trade_idea
