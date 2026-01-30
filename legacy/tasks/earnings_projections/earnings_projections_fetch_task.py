from typing import Optional, Dict, Any
from legacy.research.earnings_projections.earnings_projections_models import EarningsProjectionData
from legacy.research.earnings_projections.earnings_projections_util import get_earnings_projection_data_for_symbol
import logging
import json

logger = logging.getLogger(__name__)


async def earnings_projections_fetch_task(
    symbol: str,
    historical_earnings_analysis: Optional[Dict[str, Any]] = None,
    financial_statements_analysis: Optional[Dict[str, Any]] = None
) -> EarningsProjectionData:
    """
    Task to fetch comprehensive data needed for independent earnings projections.
    
    Args:
        symbol: Stock symbol to research
        historical_earnings_analysis: Optional historical earnings analysis results
        financial_statements_analysis: Optional financial statements analysis results
    Returns:
        EarningsProjectionData containing all necessary data for projections
    """
    logger.info(f"Fetching earnings projection data for {symbol}")

    projection_data = get_earnings_projection_data_for_symbol(
        symbol, 
        historical_earnings_analysis, 
        financial_statements_analysis
    )
    
    logger.info(f"Earnings projection data fetched for {symbol}: "
               f"{len(projection_data.quarterly_income_statements)} quarterly statements, "
               f"{len(projection_data.annual_income_statements)} annual statements")

    logger.debug(f"Earnings projection data fetched for {symbol}: {json.dumps(projection_data.model_dump(), indent=2)}")

    return projection_data