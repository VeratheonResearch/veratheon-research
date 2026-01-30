from legacy.research.earnings_projections.earnings_projections_models import EarningsProjectionAnalysis
from src.lib.supabase_cache import get_supabase_cache
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

async def earnings_projections_reporting_task(
    symbol: str, 
    earnings_projections_analysis: EarningsProjectionAnalysis
) -> None:
    """
    Reporting task to write JSON dump of earnings projections analysis results to file and cache to Redis.
    
    Args:
        symbol: Stock symbol being analyzed
        earnings_projections_analysis: EarningsProjectionAnalysis model to report
    """
    logger.info(f"Earnings Projections Reporting for {symbol}")
    
    # Cache the analysis in Redis (24 hour TTL for reports)
    cache = get_supabase_cache()
    cache.cache_report("earnings_projections", symbol, earnings_projections_analysis, ttl=86400)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"earnings_projections_{symbol}_{timestamp}.json"
    filepath = Path("reports") / filename
    
    # Write JSON to file
    with open(filepath, 'w') as f:
        json.dump(earnings_projections_analysis.model_dump(), f, indent=2)
    
    logger.info(f"Earnings Projections report written to: {filepath.absolute()}")