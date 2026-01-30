from legacy.tasks.financial_statements.financial_statements_fetch_task import financial_statements_fetch_task
from legacy.tasks.financial_statements.financial_statements_analysis_task import financial_statements_analysis_task
from legacy.tasks.financial_statements.financial_statements_reporting_task import financial_statements_reporting_task
from legacy.tasks.cache_retrieval.financial_statements_cache_retrieval_task import financial_statements_cache_retrieval_task
from legacy.research.financial_statements.financial_statements_models import FinancialStatementsData, FinancialStatementsAnalysis
import logging
import time

logger = logging.getLogger(__name__)

async def financial_statements_flow(symbol: str, force_recompute: bool = False) -> FinancialStatementsAnalysis:
    """
    Main flow for analyzing recent financial statements for changes in revenue drivers, cost structures, and working capital.
    
    This analysis directly informs the accuracy of near-term projections by examining recent operational changes
    that affect business fundamentals driving earnings.
    
    Args:
        symbol: Stock symbol to research
    Returns:
        FinancialStatementsAnalysis containing the research results and trends
    """
    start_time = time.time()
    logger.info(f"Financial statements flow started for {symbol}")
    
    # Try to get cached report first
    cached_result = await financial_statements_cache_retrieval_task(symbol, force_recompute)
    if cached_result is not None:
        logger.info(f"Returning cached financial statements analysis for {symbol}")
        return cached_result
    
    logger.info(f"No cached data found, running fresh financial statements analysis for {symbol}")
    
    # Fetch financial statements data from Alpha Vantage
    financial_data: FinancialStatementsData = await financial_statements_fetch_task(symbol)

    # Perform financial statements analysis
    financial_analysis: FinancialStatementsAnalysis = await financial_statements_analysis_task(
        symbol, financial_data
    )

    # Generate reporting output
    await financial_statements_reporting_task(symbol, financial_analysis)

    logger.info(f"Financial statements flow completed for {symbol} in {int(time.time() - start_time)} seconds")
    

    return financial_analysis