from legacy.research.company_overview.company_overview_models import CompanyOverviewAnalysis
import logging
import json
import os
from typing import Optional

logger = logging.getLogger(__name__)

async def company_overview_cache_retrieval_task(symbol: str, force_recompute: bool = False) -> Optional[CompanyOverviewAnalysis]:
    """
    Task to retrieve cached company overview analysis results.
    
    Args:
        symbol: Stock symbol to retrieve cached data for
        force_recompute: If True, skip cache retrieval and return None
        
    Returns:
        Optional[CompanyOverviewAnalysis]: Cached analysis if available and valid, None otherwise
    """
    if force_recompute:
        logger.info(f"Skipping cache retrieval for company overview analysis of {symbol} (force_recompute=True)")
        return None
    
    cache_file_path = f"output/{symbol}/company_overview_analysis.json"
    
    if not os.path.exists(cache_file_path):
        logger.info(f"No cached company overview analysis found for {symbol}")
        return None
    
    try:
        with open(cache_file_path, 'r') as f:
            cached_data = json.load(f)
        
        # Validate that we can reconstruct the analysis object
        analysis = CompanyOverviewAnalysis(**cached_data)
        
        logger.info(f"Successfully retrieved cached company overview analysis for {symbol}")
        return analysis
        
    except (json.JSONDecodeError, FileNotFoundError, TypeError, ValueError) as e:
        logger.warning(f"Failed to load cached company overview analysis for {symbol}: {e}")
        return None