from legacy.research.financial_statements.financial_statements_models import FinancialStatementsData
from legacy.research.financial_statements.financial_statements_util import get_financial_statements_data_for_symbol
import logging
import json

logger = logging.getLogger(__name__)


async def financial_statements_fetch_task(symbol: str) -> FinancialStatementsData:
    """
    Task to fetch financial statements data from Alpha Vantage for analysis.
    
    Args:
        symbol: Stock symbol to research
    Returns:
        FinancialStatementsData containing income statements, balance sheets, and cash flow statements
    """
    logger.info(f"Fetching financial statements data for {symbol}")

    financial_data: FinancialStatementsData = get_financial_statements_data_for_symbol(symbol)
    
    logger.info(f"Financial statements data fetched for {symbol}: "
               f"{len(financial_data.income_statements)} income statements, "
               f"{len(financial_data.balance_sheets)} balance sheets, "
               f"{len(financial_data.cash_flow_statements)} cash flow statements")

    logger.debug(f"Financial statements data fetched for {symbol}: {json.dumps(financial_data.model_dump(), indent=2)}")

    return financial_data