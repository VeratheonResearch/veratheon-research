from legacy.research.common.models.peer_group import PeerGroup
from legacy.research.common.peer_group_agent import peer_group_chatcompletion
import logging
import json

logger = logging.getLogger(__name__)

async def forward_pe_peer_group_task(symbol: str) -> PeerGroup:
    """
    Task to fetch the peer group for the forward PE research for a given symbol.
    
    Args:
        symbol: Stock symbol to research
    Returns:
        PeerGroup containing the peer group
    """
    logger.info(f"Fetching peer group for {symbol}")

    peer_group: PeerGroup = await peer_group_chatcompletion(symbol)

    logger.info(f"Peer group for {symbol}: {json.dumps(peer_group.model_dump(), indent=2)}")

    return peer_group