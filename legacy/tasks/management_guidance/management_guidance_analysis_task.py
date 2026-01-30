from legacy.research.management_guidance.management_guidance_models import ManagementGuidanceData, ManagementGuidanceAnalysis
from legacy.research.management_guidance.management_guidance_agent import management_guidance_agent
from typing import Optional, Any
import logging
import json

logger = logging.getLogger(__name__)

async def management_guidance_analysis_task(
    symbol: str,
    guidance_data: ManagementGuidanceData,
    historical_earnings_analysis: Optional[Any] = None,
    financial_statements_analysis: Optional[Any] = None
) -> ManagementGuidanceAnalysis:
    """
    Task to analyze management guidance for qualitative risks and opportunities.
    
    Args:
        symbol: Stock symbol being analyzed
        guidance_data: Management guidance data including transcripts and estimates
        historical_earnings_analysis: Optional historical earnings patterns for context
        financial_statements_analysis: Optional recent financial trends for context
        
    Returns:
        ManagementGuidanceAnalysis with extracted guidance indicators
    """
    logger.info(f"Analyzing management guidance for {symbol}")

    guidance_analysis = await management_guidance_agent(
        symbol, guidance_data, historical_earnings_analysis, financial_statements_analysis
    )
    
    if guidance_analysis.transcript_available:
        logger.info(f"Management guidance analysis completed for {symbol}")
    else:
        logger.warning(f"Management guidance analysis for {symbol}: No transcript available")

    logger.debug(f"Management guidance analysis for {symbol}: {json.dumps(guidance_analysis.model_dump(), indent=2)}")

    return guidance_analysis