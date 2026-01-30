from legacy.research.management_guidance.management_guidance_models import ManagementGuidanceData
from legacy.research.management_guidance.management_guidance_util import get_management_guidance_data_for_symbol
import logging
import json

logger = logging.getLogger(__name__)

async def management_guidance_fetch_task(symbol: str) -> ManagementGuidanceData:
    """
    Task to fetch management guidance data including earnings estimates and transcripts.
    
    Args:
        symbol: Stock symbol to research
        
    Returns:
        ManagementGuidanceData containing earnings estimates and latest transcript
    """
    logger.info(f"Fetching management guidance data for {symbol}")

    guidance_data = get_management_guidance_data_for_symbol(symbol)
    
    if guidance_data.earnings_transcript:
        logger.info(f"Management guidance data fetched for {symbol}: transcript available for Q{guidance_data.quarter}")
    else:
        logger.warning(f"Management guidance data fetched for {symbol}: no transcript available")

    logger.debug(f"Management guidance data fetched for {symbol}: {json.dumps(guidance_data.model_dump(), indent=2)}")

    return guidance_data