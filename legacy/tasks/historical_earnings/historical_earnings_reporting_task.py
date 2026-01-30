from legacy.research.historical_earnings.historical_earnings_models import HistoricalEarningsAnalysis
from src.lib.supabase_cache import get_supabase_cache
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

async def historical_earnings_reporting_task(
    symbol: str, 
    historical_analysis: HistoricalEarningsAnalysis
) -> None:
    """
    Reporting task to write JSON dump of historical earnings analysis results to file and cache to Redis.
    
    Args:
        symbol: Stock symbol being analyzed
        historical_analysis: HistoricalEarningsAnalysis model to report
    """
    logger.info(f"Historical Earnings Reporting for {symbol}")
    
    # Cache the analysis in Redis (24 hour TTL for reports)
    cache = get_supabase_cache()
    cache.cache_report("historical_earnings", symbol, historical_analysis, ttl=86400)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"historical_earnings_{symbol}_{timestamp}.json"
    filepath = Path("reports") / filename
    
    # Write JSON to file
    with open(filepath, 'w') as f:
        json.dump(historical_analysis.model_dump(), f, indent=2)
    
    logger.info(f"Historical Earnings report written to: {filepath.absolute()}")