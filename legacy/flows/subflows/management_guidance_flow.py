from legacy.tasks.management_guidance.management_guidance_fetch_task import management_guidance_fetch_task
from legacy.tasks.management_guidance.management_guidance_analysis_task import management_guidance_analysis_task
from legacy.tasks.management_guidance.management_guidance_reporting_task import management_guidance_reporting_task
from legacy.tasks.cache_retrieval.management_guidance_cache_retrieval_task import management_guidance_cache_retrieval_task
from legacy.research.management_guidance.management_guidance_models import ManagementGuidanceData, ManagementGuidanceAnalysis
from typing import Optional, Any
import logging
import time

logger = logging.getLogger(__name__)

async def management_guidance_flow(
    symbol: str,
    historical_earnings_analysis: Optional[Any] = None,
    financial_statements_analysis: Optional[Any] = None,
    force_recompute: bool = False
) -> ManagementGuidanceAnalysis:
    """
    Main flow for analyzing management guidance from earnings calls.
    
    This flow extracts qualitative risks and opportunities from earnings call transcripts
    to cross-check against consensus estimates and provide validation signals for 
    independent earnings analysis.
    
    Args:
        symbol: Stock symbol to research
        historical_earnings_analysis: Optional historical earnings patterns for context
        financial_statements_analysis: Optional recent financial trends for context
        
    Returns:
        ManagementGuidanceAnalysis containing guidance indicators and validation signals
    """
    
    start_time = time.time()
    logger.info(f"Management Guidance flow started for {symbol}")
    
    # Try to get cached report first
    cached_result = await management_guidance_cache_retrieval_task(symbol, historical_earnings_analysis, financial_statements_analysis, force_recompute)
    if cached_result is not None:
        logger.info(f"Returning cached management guidance analysis for {symbol}")
        return cached_result
    
    logger.info(f"No cached data found, running fresh management guidance analysis for {symbol}")
    
    # Fetch management guidance data (earnings estimates + transcripts)
    guidance_data: ManagementGuidanceData = await management_guidance_fetch_task(symbol)

    # Analyze management guidance for risks, opportunities, and signals
    guidance_analysis: ManagementGuidanceAnalysis = await management_guidance_analysis_task(
        symbol, guidance_data, historical_earnings_analysis, financial_statements_analysis
    )

    # Generate reporting output
    await management_guidance_reporting_task(symbol, guidance_analysis)

    logger.info(f"Management Guidance flow completed for {symbol} in {int(time.time() - start_time)} seconds")
    

    return guidance_analysis