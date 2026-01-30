from typing import Optional
from pydantic import BaseModel


class GlobalQuoteData(BaseModel):
    symbol: str
    price: Optional[str] = None