from legacy.tasks.forward_pe.forward_pe_fetch_earnings_task import forward_pe_fetch_single_earnings_task, forward_pe_fetch_earnings_for_symbols_task
from legacy.tasks.forward_pe.forward_pe_analysis_task import forward_pe_analysis_task
from legacy.tasks.forward_pe.forward_pe_sanity_check_task import forward_pe_sanity_check_task
from legacy.tasks.forward_pe.forward_pe_reporting_task import forward_pe_valuation_reporting_task, forward_pe_sanity_check_reporting_task
from legacy.tasks.cache_retrieval.forward_pe_cache_retrieval_task import forward_pe_valuation_cache_retrieval_task, forward_pe_sanity_check_cache_retrieval_task
from legacy.research.forward_pe.forward_pe_models import ForwardPeValuation, ForwardPEEarningsSummary, ForwardPeSanityCheck
from legacy.research.common.models.peer_group import PeerGroup
from typing import Optional, Any
import logging
import time

logger = logging.getLogger(__name__)

async def forward_pe_flow(
    symbol: str,
    peer_group: PeerGroup,
    earnings_projections_analysis: Optional[Any] = None,
    management_guidance_analysis: Optional[Any] = None,
    forward_pe_sanity_check: Optional[ForwardPeSanityCheck] = None,
    force_recompute: bool = False,
) -> ForwardPeValuation:
    """
    Main flow for running forward PE analysis.
    
    Args:
        symbol: Stock symbol to research
        peer_group: Peer group of the symbol
        earnings_projections_analysis: Optional independent earnings projections for validation
        management_guidance_analysis: Optional management guidance analysis for context
        forward_pe_sanity_check: Optional sanity check results for validation
    Returns:
        ForwardPeValuation containing the research results and metadata
    """
    
    start_time = time.time()
    logger.info(f"Forward PE flow started for {symbol}")
    
    # Try to get cached report first
    cached_result = await forward_pe_valuation_cache_retrieval_task(symbol, peer_group, earnings_projections_analysis, management_guidance_analysis, forward_pe_sanity_check, force_recompute)
    if cached_result is not None:
        logger.info(f"Returning cached forward PE valuation analysis for {symbol}")
        return cached_result
    
    logger.info(f"No cached data found, running fresh forward PE valuation analysis for {symbol}")
    
    # Get the earnings data for the user's symbol and its peer group
    earnings_summary: ForwardPEEarningsSummary = await forward_pe_fetch_earnings_for_symbols_task(peer_group.original_symbol, peer_group.peer_group)

    # Perform forward PE analysis
    forward_pe_valuation: ForwardPeValuation = await forward_pe_analysis_task(
        peer_group.original_symbol, 
        earnings_summary, 
        earnings_projections_analysis,
        management_guidance_analysis, 
        forward_pe_sanity_check
    )

    # Generate reporting output
    await forward_pe_valuation_reporting_task(symbol, forward_pe_valuation)

    logger.info(f"Forward PE flow completed for {symbol}")
    logger.info(f"Forward PE flow completed for {symbol} in {int(time.time() - start_time)} seconds")
    

    return forward_pe_valuation


async def forward_pe_sanity_check_flow(
    symbol: str,
    force_recompute: bool = False,
) -> ForwardPeSanityCheck:
    """
    Main flow for running forward PE sanity check.
    
    Args:
        symbol: Stock symbol to research
    Returns:
        ForwardPeSanityCheck containing the research results and metadata
    """
    
    start_time = time.time()
    logger.info(f"Forward PE sanity check flow started for {symbol}")
    
    # Try to get cached report first
    cached_result = await forward_pe_sanity_check_cache_retrieval_task(symbol, force_recompute)
    if cached_result is not None:
        logger.info(f"Returning cached forward PE sanity check analysis for {symbol}")
        return cached_result
    
    logger.info(f"No cached data found, running fresh forward PE sanity check analysis for {symbol}")
    
    # Get the earnings data for the user's symbol and its peer group
    earnings_summary: ForwardPEEarningsSummary = await forward_pe_fetch_single_earnings_task(symbol)

    # Perform forward PE sanity check
    forward_pe_sanity_check: ForwardPeSanityCheck = await forward_pe_sanity_check_task(earnings_summary)

    # Generate reporting output
    await forward_pe_sanity_check_reporting_task(symbol, forward_pe_sanity_check)

    logger.info(f"Forward PE sanity check flow completed for {symbol} in {int(time.time() - start_time)} seconds")
    

    return forward_pe_sanity_check
