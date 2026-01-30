from typing import Optional, Dict, Any
from legacy.tasks.earnings_projections.earnings_projections_fetch_task import earnings_projections_fetch_task
from legacy.tasks.earnings_projections.earnings_projections_analysis_task import earnings_projections_analysis_task
from legacy.tasks.earnings_projections.earnings_projections_reporting_task import earnings_projections_reporting_task
from legacy.tasks.cache_retrieval.earnings_projections_cache_retrieval_task import earnings_projections_cache_retrieval_task
from legacy.research.earnings_projections.earnings_projections_models import EarningsProjectionData, EarningsProjectionAnalysis
import logging
import time

logger = logging.getLogger(__name__)


async def earnings_projections_flow(
    symbol: str,
    historical_earnings_analysis: Optional[Dict[str, Any]] = None,
    financial_statements_analysis: Optional[Dict[str, Any]] = None,
    force_recompute: bool = False
) -> EarningsProjectionAnalysis:
    """
    Main flow for creating independent earnings projections for next quarter validation.
    
    This flow creates your own baseline estimate that's foundational for independently 
    challenging consensus, enabling true validation by providing an independent analytical baseline.
    
    Args:
        symbol: Stock symbol to research
        historical_earnings_analysis: Optional historical earnings analysis results
        financial_statements_analysis: Optional financial statements analysis results
    Returns:
        EarningsProjectionAnalysis containing independent projections and consensus validation
    """
    start_time = time.time()
    logger.info(f"Independent Earnings Projections flow started for {symbol}")
    
    # Try to get cached report first
    cached_result = await earnings_projections_cache_retrieval_task(symbol, historical_earnings_analysis, financial_statements_analysis, force_recompute)
    if cached_result is not None:
        logger.info(f"Returning cached earnings projections analysis for {symbol}")
        return cached_result
    
    logger.info(f"No cached data found, running fresh earnings projections analysis for {symbol}")
    
    # Fetch comprehensive data for earnings projections
    projection_data: EarningsProjectionData = await earnings_projections_fetch_task(
        symbol, historical_earnings_analysis, financial_statements_analysis
    )

    # Perform independent earnings projections analysis
    projections_analysis: EarningsProjectionAnalysis = await earnings_projections_analysis_task(
        symbol, projection_data
    )

    # Generate reporting output
    await earnings_projections_reporting_task(symbol, projections_analysis)

    logger.info(f"Independent Earnings Projections flow completed for {symbol} in {int(time.time() - start_time)} seconds")
    

    return projections_analysis