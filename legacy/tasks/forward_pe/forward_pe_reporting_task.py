from legacy.research.forward_pe.forward_pe_models import ForwardPeValuation, ForwardPeSanityCheck
from src.lib.supabase_cache import get_supabase_cache
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

async def forward_pe_valuation_reporting_task(
    symbol: str, 
    forward_pe_valuation: ForwardPeValuation
) -> None:
    """
    Reporting task to write JSON dump of forward PE valuation analysis results to file and cache to Redis.
    
    Args:
        symbol: Stock symbol being analyzed
        forward_pe_valuation: ForwardPeValuation model to report
    """
    logger.info(f"Forward PE Valuation Reporting for {symbol}")
    
    # Cache the analysis in Redis (24 hour TTL for reports)
    cache = get_supabase_cache()
    cache.cache_report("forward_pe_valuation", symbol, forward_pe_valuation, ttl=86400)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"forward_pe_valuation_{symbol}_{timestamp}.json"
    filepath = Path("reports") / filename
    
    # Write JSON to file
    with open(filepath, 'w') as f:
        json.dump(forward_pe_valuation.model_dump(), f, indent=2)
    
    logger.info(f"Forward PE Valuation report written to: {filepath.absolute()}")

async def forward_pe_sanity_check_reporting_task(
    symbol: str, 
    forward_pe_sanity_check: ForwardPeSanityCheck
) -> None:
    """
    Reporting task to write JSON dump of forward PE sanity check results to file and cache to Redis.
    
    Args:
        symbol: Stock symbol being analyzed
        forward_pe_sanity_check: ForwardPeSanityCheck model to report
    """
    logger.info(f"Forward PE Sanity Check Reporting for {symbol}")
    
    # Cache the analysis in Redis (24 hour TTL for reports)
    cache = get_supabase_cache()
    cache.cache_report("forward_pe_sanity_check", symbol, forward_pe_sanity_check, ttl=86400)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"forward_pe_sanity_check_{symbol}_{timestamp}.json"
    filepath = Path("reports") / filename
    
    # Write JSON to file
    with open(filepath, 'w') as f:
        json.dump(forward_pe_sanity_check.model_dump(), f, indent=2)
    
    logger.info(f"Forward PE Sanity Check report written to: {filepath.absolute()}")