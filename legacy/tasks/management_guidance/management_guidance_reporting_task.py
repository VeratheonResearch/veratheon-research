from legacy.research.management_guidance.management_guidance_models import ManagementGuidanceAnalysis
from src.lib.supabase_cache import get_supabase_cache
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

async def management_guidance_reporting_task(
    symbol: str, 
    management_guidance_analysis: ManagementGuidanceAnalysis
) -> None:
    """
    Reporting task to write JSON dump of management guidance analysis results to file and cache to Redis.
    
    Args:
        symbol: Stock symbol being analyzed
        management_guidance_analysis: ManagementGuidanceAnalysis model to report
    """
    logger.info(f"Management Guidance Reporting for {symbol}")
    
    # Cache the analysis in Redis (24 hour TTL for reports)
    cache = get_supabase_cache()
    cache.cache_report("management_guidance", symbol, management_guidance_analysis, ttl=86400)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"management_guidance_{symbol}_{timestamp}.json"
    filepath = Path("reports") / filename
    
    # Write JSON to file
    with open(filepath, 'w') as f:
        json.dump(management_guidance_analysis.model_dump(), f, indent=2)
    
    logger.info(f"Management Guidance report written to: {filepath.absolute()}")