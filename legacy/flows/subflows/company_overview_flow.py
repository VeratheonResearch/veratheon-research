from legacy.tasks.company_overview.company_overview_fetch_task import company_overview_fetch_task
from legacy.tasks.company_overview.company_overview_analysis_task import company_overview_analysis_task
from legacy.tasks.company_overview.company_overview_reporting_task import company_overview_reporting_task
from legacy.tasks.cache_retrieval.company_overview_cache_retrieval_task import company_overview_cache_retrieval_task
from legacy.research.company_overview.company_overview_models import CompanyOverviewData, CompanyOverviewAnalysis
import logging
import time

logger = logging.getLogger(__name__)

async def company_overview_flow(symbol: str, force_recompute: bool = False) -> CompanyOverviewAnalysis:
    """
    Main flow for running company overview analysis.
    
    Fetches comprehensive company overview data from Alpha Vantage and provides
    structured analysis of business fundamentals, competitive positioning, and key metrics.
    
    Args:
        symbol: Stock symbol to research
        force_recompute: If True, skip cache and recompute analysis
    Returns:
        CompanyOverviewAnalysis containing the research results and business insights
    """
    
    start_time = time.time()
    logger.info(f"Company Overview flow started for {symbol}")
    
    # Try to get cached report first
    cached_result = await company_overview_cache_retrieval_task(symbol, force_recompute)
    if cached_result is not None:
        logger.info(f"Returning cached company overview analysis for {symbol}")
        return cached_result
    
    logger.info(f"No cached data found, running fresh company overview analysis for {symbol}")
    
    # Fetch company overview data from Alpha Vantage
    company_data: CompanyOverviewData = await company_overview_fetch_task(symbol)

    # Perform company overview analysis
    company_analysis: CompanyOverviewAnalysis = await company_overview_analysis_task(
        symbol, company_data
    )

    # Generate reporting output
    await company_overview_reporting_task(symbol, company_analysis)

    logger.info(f"Company Overview flow completed for {symbol} in {int(time.time() - start_time)} seconds")
    

    return company_analysis