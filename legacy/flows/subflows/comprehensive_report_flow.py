import logging
from typing import Dict, Any
import time
from legacy.tasks.comprehensive_report.comprehensive_report_task import comprehensive_report_task
from legacy.tasks.comprehensive_report.comprehensive_report_reporting_task import comprehensive_report_reporting_task
from legacy.tasks.cache_retrieval.comprehensive_report_cache_retrieval_task import comprehensive_report_cache_retrieval_task
from legacy.research.comprehensive_report.comprehensive_report_models import ComprehensiveReport

logger = logging.getLogger(__name__)


async def comprehensive_report_flow(
    symbol: str,
    all_analyses: Dict[str, Any],
    force_recompute: bool = False
) -> ComprehensiveReport:
    """
    Generate comprehensive report from all analysis results.
    This subflow synthesizes all research into a single readable report.
    
    Args:
        symbol: Stock symbol
        all_analyses: Dictionary containing all analysis results
        force_recompute: Whether to bypass cache and regenerate
        
    Returns:
        ComprehensiveReport: Synthesized report ready for UI consumption
    """
    
    start_time = time.time()
    logger.info(f"Comprehensive report flow started for {symbol}")
    
    # Try to get cached report first
    cached_result = await comprehensive_report_cache_retrieval_task(symbol, all_analyses, force_recompute)
    if cached_result is not None:
        logger.info(f"Returning cached comprehensive report for {symbol}")
        return cached_result
    
    logger.info(f"No cached data found, running fresh comprehensive report analysis for {symbol}")
    
    comprehensive_report = await comprehensive_report_task(symbol, all_analyses)
    
    # Generate reporting output
    await comprehensive_report_reporting_task(symbol, comprehensive_report)
    
    logger.info(f"Comprehensive report flow completed for {symbol} in {int(time.time() - start_time)} seconds")
    
    
    return comprehensive_report