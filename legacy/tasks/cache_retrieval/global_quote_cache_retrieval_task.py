from legacy.research.global_quote.global_quote_models import GlobalQuoteData
import logging
import json
import os
from typing import Optional

logger = logging.getLogger(__name__)

async def global_quote_cache_retrieval_task(symbol: str, force_recompute: bool = False) -> Optional[GlobalQuoteData]:
    """
    Task to retrieve cached global quote data.
    
    Args:
        symbol: Stock symbol to retrieve cached data for
        force_recompute: If True, skip cache retrieval and return None
        
    Returns:
        Optional[GlobalQuoteData]: Cached data if available and valid, None otherwise
    """
    if force_recompute:
        logger.info(f"Skipping cache retrieval for global quote data of {symbol} (force_recompute=True)")
        return None
    
    cache_file_path = f"output/{symbol}/global_quote_data.json"
    
    if not os.path.exists(cache_file_path):
        logger.info(f"No cached global quote data found for {symbol}")
        return None
    
    try:
        with open(cache_file_path, 'r') as f:
            cached_data = json.load(f)
        
        # Validate that we can reconstruct the data object
        quote_data = GlobalQuoteData(**cached_data)
        
        logger.info(f"Successfully retrieved cached global quote data for {symbol}")
        return quote_data
        
    except (json.JSONDecodeError, FileNotFoundError, TypeError, ValueError) as e:
        logger.warning(f"Failed to load cached global quote data for {symbol}: {e}")
        return None