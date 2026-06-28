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


class CompanyOverview(BaseModel):
    """A company's profile/overview information."""

    symbol: str
    organ_name: str | None = None
    organ_short_name: str | None = None
    sector: str | None = None
    company_profile: str | None = None
    listing_date: str | None = None
    issue_share: int | None = None


class Shareholder(BaseModel):
    """A single shareholder entry from a company's shareholder list."""

    symbol: str
    share_holder: str
    quantity: int | None = None
    share_own_percent: float | None = None
    update_date: str | None = None


class Officer(BaseModel):
    """A company officer/board member."""

    symbol: str
    officer_name: str
    officer_position: str | None = None
    officer_own_percent: float | None = None
    officer_own_quantity: int | None = None


class Subsidiary(BaseModel):
    """A subsidiary or affiliate company."""

    symbol: str
    organ_name: str
    ownership_percent: float | None = None
    sub_organ_code: str | None = None
    type: str | None = None  # "subsidiary" | "affiliate"


class CompanyEvent(BaseModel):
    """A corporate event (dividend, AGM, ownership change, ...)."""

    symbol: str
    event_title: str | None = None
    event_code: str | None = None
    public_date: str | None = None
    record_date: str | None = None
    exright_date: str | None = None


class NewsItem(BaseModel):
    """A news article related to a company."""

    symbol: str
    title: str
    public_date: str | None = None
    source: str | None = None


class FinancialRow(BaseModel):
    """A single line item in a financial report, in long format.

    Long format lets one model represent balance sheet / income statement /
    cashflow / ratio rows from any source without per-source wide schemas.
    """

    symbol: str
    statement: str  # 'balance_sheet' | 'income_statement' | 'cashflow' | 'ratio_summary' | ...
    period: str | None = None
    item_code: str | None = None
    item_name: str
    value: float | None = None
    unit: str | None = "VND"
    parent_code: str | None = None
