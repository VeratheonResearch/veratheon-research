from legacy.research.financial_statements.financial_statements_models import FinancialStatementsData, FinancialStatementsAnalysis
from legacy.research.financial_statements.financial_statements_agent import financial_statements_analysis_agent
from agents import Runner, RunResult
from src.lib.token_logger_hook import TokenLoggerHook
import json
import logging

logger = logging.getLogger(__name__)


async def financial_statements_analysis_task(
    symbol: str, 
    financial_data: FinancialStatementsData
) -> FinancialStatementsAnalysis:
    """
    Task to perform financial statements analysis for changes in revenue drivers, cost structures, and working capital.
    
    Args:
        symbol: Stock symbol to research
        financial_data: Financial statements data from Alpha Vantage
    Returns:
        FinancialStatementsAnalysis containing the analysis results and trends
    """
    logger.info(f"Performing financial statements analysis for {symbol}")

    # Prepare the input for the agent
    input_data = f"""
    symbol: {symbol}
    financial_statements_data: {financial_data.model_dump_json()}
    """

    result: RunResult = await Runner.run(
        financial_statements_analysis_agent,
        input=input_data,
        hooks=TokenLoggerHook(symbol=symbol)
    )
    
    financial_analysis: FinancialStatementsAnalysis = result.final_output

    logger.debug(f"Financial statements analysis for {symbol}: {json.dumps(financial_analysis.model_dump(), indent=2)}")

    return financial_analysis