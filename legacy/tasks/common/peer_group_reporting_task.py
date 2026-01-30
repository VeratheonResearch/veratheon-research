from legacy.research.common.models.peer_group import PeerGroup
from src.lib.supabase_cache import get_supabase_cache
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

async def peer_group_reporting_task(
    symbol: str, 
    peer_group: PeerGroup
) -> None:
    """
    Reporting task to write JSON dump of peer group analysis results to file and cache to Redis.
    
    Args:
        symbol: Stock symbol being analyzed
        peer_group: PeerGroup model to report
    """
    logger.info(f"Peer Group Reporting for {symbol}")
    
    # Cache the analysis in Redis (24 hour TTL for reports)
    cache = get_supabase_cache()
    cache.cache_report("peer_group", symbol, peer_group, ttl=86400)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"peer_group_{symbol}_{timestamp}.json"
    filepath = Path("reports") / filename
    
    # Write JSON to file
    with open(filepath, 'w') as f:
        json.dump(peer_group.model_dump(), f, indent=2)
    
    logger.info(f"Peer Group report written to: {filepath.absolute()}")