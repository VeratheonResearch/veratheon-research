from legacy.research.trade_ideas.trade_idea_models import TradeIdea
from src.lib.supabase_cache import get_supabase_cache
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

async def trade_ideas_reporting_task(
    symbol: str, 
    trade_idea: TradeIdea
) -> None:
    """
    Reporting task to write JSON dump of trade ideas analysis results to file and cache to Redis.
    
    Args:
        symbol: Stock symbol being analyzed
        trade_idea: TradeIdea model to report
    """
    logger.info(f"Trade Ideas Reporting for {symbol}")
    
    # Cache the analysis in Redis (24 hour TTL for reports)
    cache = get_supabase_cache()
    cache.cache_report("trade_ideas", symbol, trade_idea, ttl=86400)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trade_ideas_{symbol}_{timestamp}.json"
    filepath = Path("reports") / filename
    
    # Write JSON to file
    with open(filepath, 'w') as f:
        json.dump(trade_idea.model_dump(), f, indent=2)
    
    logger.info(f"Trade Ideas report written to: {filepath.absolute()}")