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


class Tick(BaseModel):
    """A single matched-order tick from intraday trading data."""

    symbol: str
    time: datetime
    price: float
    volume: int
    match_type: str | None = None


class Industry(BaseModel):
    """An ICB sector classification code."""

    icb_code: str
    icb_name: str
    en_icb_name: str | None = None
    level: int


class SymbolIndustry(BaseModel):
    """A symbol's ICB sector classification, one row per ICB level."""

    symbol: str
    organ_name: str | None = None
    com_type_code: str | None = None
    icb_level: int
    icb_code: str
    icb_name: str
