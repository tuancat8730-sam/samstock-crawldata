from datetime import datetime

from pydantic import BaseModel


class Symbol(BaseModel):
    """A listed stock symbol, normalized across providers."""

    symbol: str
    exchange: str
    organ_name: str | None = None
    type: str | None = None


class Bar(BaseModel):
    """A single OHLCV bar for a symbol, normalized across providers."""

    symbol: str
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
