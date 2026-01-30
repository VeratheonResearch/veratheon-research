from legacy.research.cross_reference.cross_reference_agent import cross_reference_agent
from agents import Runner, RunResult
from src.lib.token_logger_hook import TokenLoggerHook
import json
import logging
from typing import List, Any
from legacy.research.cross_reference.cross_reference_models import CrossReferencedAnalysisCompletion

logger = logging.getLogger(__name__)

async def cross_reference_task(
    symbol: str, 
    original_analysis_type: str,
    original_analysis: Any,
    data_points: List[Any]
) -> CrossReferencedAnalysisCompletion:
    """
    Task to perform cross reference analysis for a given symbol.
    
    Args:
        symbol: Stock symbol to research
        original_analysis_type: Type of original analysis for the symbol
        original_analysis: Original analysis for the symbol
        data_points: List of data points to cross reference against
    Returns:
        CrossReferencedAnalysisResponse containing the cross reference analysis
    """
    logger.info(f"Performing cross reference analysis for original analysis: {original_analysis_type}")

    # Build input with optional context
    input_data = f"original_symbol: {symbol}, original_analysis_type: {original_analysis_type}, original_analysis: {original_analysis}, data_points: {data_points}"

    result: RunResult = await Runner.run(
        cross_reference_agent,
        input=input_data,
        hooks=TokenLoggerHook(symbol=symbol)
    )
    cross_reference: CrossReferencedAnalysisCompletion = result.final_output

    logger.debug(f"Cross reference for original analysis: {original_analysis}: {json.dumps(cross_reference.model_dump(), indent=2)}")

    return cross_reference
