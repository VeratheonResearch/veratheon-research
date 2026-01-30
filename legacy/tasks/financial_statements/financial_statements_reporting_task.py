from legacy.research.financial_statements.financial_statements_models import FinancialStatementsAnalysis
from src.lib.supabase_cache import get_supabase_cache
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

async def financial_statements_reporting_task(
    symbol: str, 
    financial_analysis: FinancialStatementsAnalysis
) -> None:
    """
    Reporting task to write JSON dump of financial statements analysis results to file and cache to Redis.
    
    Args:
        symbol: Stock symbol being analyzed
        financial_analysis: FinancialStatementsAnalysis model to report
    """
    logger.info(f"Financial Statements Reporting for {symbol}")
    
    # Cache the analysis in Redis (24 hour TTL for reports)
    cache = get_supabase_cache()
    cache.cache_report("financial_statements", symbol, financial_analysis, ttl=86400)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"financial_statements_{symbol}_{timestamp}.json"
    filepath = Path("reports") / filename
    
    # Write JSON to file
    with open(filepath, 'w') as f:
        json.dump(financial_analysis.model_dump(), f, indent=2)
    
    logger.info(f"Financial Statements report written to: {filepath.absolute()}")