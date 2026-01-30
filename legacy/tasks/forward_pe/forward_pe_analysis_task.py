from legacy.research.forward_pe.forward_pe_models import ForwardPeValuation
from legacy.research.forward_pe.forward_pe_analysis_agent import forward_pe_analysis_agent
from agents import Runner, RunResult
from src.lib.token_logger_hook import TokenLoggerHook
from legacy.research.forward_pe.forward_pe_models import ForwardPEEarningsSummary
import json
import logging
from typing import Optional, Any

logger = logging.getLogger(__name__)

async def forward_pe_analysis_task(
    symbol: str, 
    earnings_summary: ForwardPEEarningsSummary,
    earnings_projections_analysis: Optional[Any] = None,
    management_guidance_analysis: Optional[Any] = None,
    forward_pe_sanity_check: Optional[Any] = None
) -> ForwardPeValuation:
    """
    Task to perform forward PE analysis for the forward PE research for a given symbol.
    
    Args:
        symbol: Stock symbol to research
        earnings_summary: Earnings summary for the symbol
        earnings_projections_analysis: Optional independent earnings projections for validation
        management_guidance_analysis: Optional management guidance analysis for context
        forward_pe_sanity_check: Optional sanity check results for validation
    Returns:
        ForwardPeValuation containing the forward PE analysis
    """
    logger.info(f"Performing forward PE analysis for {symbol}")

    # Build input with optional context
    input_data = f"original_symbol: {symbol}, earnings_summary: {earnings_summary}"
    if earnings_projections_analysis:
        input_data += f", earnings_projections_analysis: {earnings_projections_analysis}"
    if management_guidance_analysis:
        input_data += f", management_guidance_analysis: {management_guidance_analysis}"
    if forward_pe_sanity_check:
        input_data += f", forward_pe_sanity_check: {forward_pe_sanity_check}"

    result: RunResult = await Runner.run(
        forward_pe_analysis_agent,
        input=input_data,
        hooks=TokenLoggerHook(symbol=symbol)
    )
    forward_pe_analysis: ForwardPeValuation = result.final_output

    logger.debug(f"Forward PE analysis for {symbol}: {json.dumps(forward_pe_analysis.model_dump(), indent=2)}")

    return forward_pe_analysis
