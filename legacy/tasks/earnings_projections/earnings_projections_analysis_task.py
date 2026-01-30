from legacy.research.earnings_projections.earnings_projections_models import EarningsProjectionData, EarningsProjectionAnalysis
from legacy.research.earnings_projections.earnings_projections_agent import earnings_projections_analysis_agent
from agents import Runner, RunResult
from src.lib.token_logger_hook import TokenLoggerHook
import json
import logging

logger = logging.getLogger(__name__)

async def earnings_projections_analysis_task(
    symbol: str, 
    projection_data: EarningsProjectionData
) -> EarningsProjectionAnalysis:
    """
    Task to perform independent earnings projections for next quarter validation.
    
    Args:
        symbol: Stock symbol to research
        projection_data: Comprehensive earnings projection data
    Returns:
        EarningsProjectionAnalysis containing independent projections and consensus validation
    """
    
    logger.info(f"Earnings Projections flow started for {symbol}")

    # Prepare the input for the agent
    input_data = f"""
    symbol: {symbol}
    earnings_projection_data: {projection_data.model_dump_json()}
    """

    result: RunResult = await Runner.run(
        earnings_projections_analysis_agent,
        input=input_data,
        hooks=TokenLoggerHook(symbol=symbol)
    )
    
    projections_analysis: EarningsProjectionAnalysis = result.final_output

    # Extract key projection metrics for logging
    next_quarter = projections_analysis.next_quarter_projection
    
    logger.info(f"Earnings Projections flow completed for {symbol}: "
               f"Projected EPS: ${next_quarter.projected_eps:.2f}, "
               f"Projected Revenue: ${next_quarter.projected_revenue:,.0f}"
    )
    
    # Log consensus comparison if available
    if next_quarter.consensus_eps_estimate:
        logger.info(f"Consensus EPS: ${next_quarter.consensus_eps_estimate:.2f}, "
                   f"Our estimate vs consensus: {next_quarter.eps_vs_consensus_percent:.1f}%")

    # Log the full analysis as JSON for development visibility
    logger.debug(f"Earnings Projections flow completed for {symbol}: {json.dumps(projections_analysis.model_dump(), indent=2)}")

    return projections_analysis