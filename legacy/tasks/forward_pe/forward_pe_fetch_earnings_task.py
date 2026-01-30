from typing import List
from legacy.research.forward_pe.forward_pe_models import ForwardPEEarningsSummary
from legacy.research.forward_pe.forward_pe_fetch_earnings_util import get_quarterly_eps_data_for_symbol, get_quarterly_eps_data_for_symbols
import logging
import json

logger = logging.getLogger(__name__)

async def forward_pe_fetch_earnings_for_symbols_task(symbol: str, peer_group: List[str]) -> ForwardPEEarningsSummary:
    """
    Task to fetch the earnings data for the forward PE research for a given symbol.
    
    Args:
        symbol: Stock symbol to research
        peer_group: List of peer symbols
    Returns:
        EarningsSummary containing the earnings data
    """
    logger.info(f"Fetching earnings data for {symbol} with peer group {peer_group}")

    earnings_summary: list(ForwardPEEarningsSummary) = get_quarterly_eps_data_for_symbols([symbol] + peer_group)

    for earnings in earnings_summary:
        logger.debug(f"Earnings data fetched for {symbol}: {json.dumps(earnings.model_dump(), indent=2)}")

    return earnings_summary


async def forward_pe_fetch_single_earnings_task(symbol: str) -> ForwardPEEarningsSummary:
    """
    Task to fetch the earnings data for the forward PE research for a given symbol.
    
    Args:
        symbol: Stock symbol to research
    Returns:
        EarningsSummary containing the earnings data
    """
    logger.info(f"Fetching earnings data for {symbol}")

    earnings_summary: ForwardPEEarningsSummary = get_quarterly_eps_data_for_symbol(symbol)

    logger.debug(f"Earnings data fetched for {symbol}: {json.dumps(earnings_summary.model_dump(), indent=2)}")

    return earnings_summary
