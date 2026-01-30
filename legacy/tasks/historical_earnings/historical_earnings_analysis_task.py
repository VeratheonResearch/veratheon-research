from legacy.research.historical_earnings.historical_earnings_models import HistoricalEarningsData, HistoricalEarningsAnalysis
from legacy.research.historical_earnings.historical_earnings_agent import historical_earnings_analysis_agent
from agents import Runner, RunResult
from src.lib.token_logger_hook import TokenLoggerHook
import json
import logging

logger = logging.getLogger(__name__)

async def historical_earnings_analysis_task(
    symbol: str,
    historical_data: HistoricalEarningsData
) -> HistoricalEarningsAnalysis:
    """
    Task to perform historical earnings analysis for patterns in beats/misses, revenue growth, and margin trends.
    
    Args:
        symbol: Stock symbol to research
        historical_data: Historical earnings data from Alpha Vantage
    Returns:
        HistoricalEarningsAnalysis containing the analysis results and patterns
    """
    logger.info(f"Performing historical earnings analysis for {symbol}")

    # Prepare the input for the agent
    input_data = f"""
    symbol: {symbol}
    historical_earnings_data: {historical_data.model_dump_json()}
    """

    logger.debug(f"Input data for historical earnings analysis for {symbol}: {input_data}")

    # Use hooks to automatically track token usage
    result: RunResult = await Runner.run(
        historical_earnings_analysis_agent,
        input=input_data,
        hooks=TokenLoggerHook(symbol=symbol)
    )

    historical_analysis: HistoricalEarningsAnalysis = result.final_output

    logger.info(f"Historical earnings analysis completed for {symbol}")

    logger.debug(f"Historical earnings analysis for {symbol}: {json.dumps(historical_analysis.model_dump(), indent=2)}")

    return historical_analysis