from legacy.research.company_overview.company_overview_models import CompanyOverviewData, CompanyOverviewAnalysis
from legacy.research.company_overview.company_overview_agent import company_overview_agent
import logging
import json

logger = logging.getLogger(__name__)

async def company_overview_analysis_task(symbol: str, company_data: CompanyOverviewData) -> CompanyOverviewAnalysis:
    """
    Task to analyze company overview data using the company overview agent.
    
    Args:
        symbol: Stock symbol being analyzed
        company_data: CompanyOverviewData to analyze
        
    Returns:
        CompanyOverviewAnalysis containing structured analysis results
    """
    logger.info(f"Starting company overview analysis for {symbol}")
    
    analysis = company_overview_agent(symbol, company_data)
    
    logger.info(f"Company overview analysis completed for {symbol}")
    logger.debug(f"Company overview analysis for {symbol}: {json.dumps(analysis.model_dump(), indent=2)}")
    
    return analysis