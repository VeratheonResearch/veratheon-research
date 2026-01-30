import json
from agents import Runner, RunResult
from src.lib.token_logger_hook import TokenLoggerHook
from legacy.research.comprehensive_report.key_insights_agent import key_insights_agent
from legacy.research.comprehensive_report.comprehensive_report_models import KeyInsights, ComprehensiveReport
import logging

logger = logging.getLogger(__name__)

async def key_insights_task(
    symbol: str,
    comprehensive_report: ComprehensiveReport
) -> KeyInsights:
    """
    Task to extract key insights from a comprehensive research report.

    Args:
        symbol: Stock symbol to research
        comprehensive_report: The full comprehensive report to extract insights from
        
    Returns:
        KeyInsights containing the most critical takeaways
    """
    logger.info(f"Generating key insights for {symbol}")

    # Build input data with the comprehensive report
    input_data = f"original_symbol: {symbol}, comprehensive_report: {comprehensive_report.model_dump()}"

    result: RunResult = await Runner.run(
        key_insights_agent,
        input=input_data,
        hooks=TokenLoggerHook(symbol=symbol)
    )
    key_insights: KeyInsights = result.final_output

    return key_insights