from legacy.research.company_overview.company_overview_models import CompanyOverviewData
from legacy.research.company_overview.company_overview_util import get_company_overview_data_for_symbol
import logging
import json

logger = logging.getLogger(__name__)

async def company_overview_fetch_task(symbol: str) -> CompanyOverviewData:
    """
    Task to fetch company overview data from Alpha Vantage.
    
    Args:
        symbol: Stock symbol to research
    Returns:
        CompanyOverviewData containing comprehensive company information
    """
    logger.info(f"Fetching company overview data for {symbol}")

    company_data = get_company_overview_data_for_symbol(symbol)
    
    logger.info(f"Company overview data fetched for {symbol}: {company_data.name}")

    logger.debug(f"Company overview data fetched for {symbol}: {json.dumps(company_data.model_dump(), indent=2)}")

    return company_data