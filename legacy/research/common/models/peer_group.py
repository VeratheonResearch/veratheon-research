from typing import List
from pydantic import BaseModel

class PeerGroup(BaseModel):
    original_symbol: str
    peer_group: List[str]