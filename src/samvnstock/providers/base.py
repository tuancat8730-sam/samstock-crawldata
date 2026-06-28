from abc import ABC, abstractmethod

from samvnstock.core.models import (
    Bar,
    CompanyEvent,
    CompanyOverview,
    FinancialRow,
    Industry,
    NewsItem,
    Officer,
    Shareholder,
    Subsidiary,
    Symbol,
    SymbolIndustry,
    Tick,
)


class ListingProvider(ABC):
    """Interface every listing source (VCI, ...) must implement.

    Only `all_symbols` is mandatory. The other methods raise
    `NotImplementedError` by default so a source can implement just the
    subset its upstream API actually supports (e.g. VND only does
    `all_symbols`) without breaking the ABC contract.
    """

    @abstractmethod
    def all_symbols(self) -> list[Symbol]: ...

    @abstractmethod
    async def all_symbols_async(self) -> list[Symbol]: ...

    def industry(self) -> list[Industry]:
        raise NotImplementedError

    async def industry_async(self) -> list[Industry]:
        raise NotImplementedError

    def symbols_by_exchange(self) -> list[Symbol]:
        raise NotImplementedError

    async def symbols_by_exchange_async(self) -> list[Symbol]:
        raise NotImplementedError

    def symbols_by_group(self, group: str) -> list[str]:
        raise NotImplementedError

    async def symbols_by_group_async(self, group: str) -> list[str]:
        raise NotImplementedError

    def symbols_by_industries(self) -> list[SymbolIndustry]:
        raise NotImplementedError

    async def symbols_by_industries_async(self) -> list[SymbolIndustry]:
        raise NotImplementedError


class QuoteProvider(ABC):
    """Interface every quote source (VCI, VND, ...) must implement.

    Only `history` is mandatory. `intraday` raises `NotImplementedError` by
    default for sources that don't support it.
    """

    @abstractmethod
    def history(self, symbol: str, start: str, end: str | None = None) -> list[Bar]: ...

    @abstractmethod
    async def history_async(
        self, symbol: str, start: str, end: str | None = None
    ) -> list[Bar]: ...

    def intraday(self, symbol: str, page_size: int = 100) -> list[Tick]:
        raise NotImplementedError

    async def intraday_async(self, symbol: str, page_size: int = 100) -> list[Tick]:
        raise NotImplementedError


class CompanyProvider(ABC):
    """Interface every company-profile source (VCI, ...) must implement.

    Only `overview` is mandatory; the other methods raise
    `NotImplementedError` by default for sources that don't support them.
    """

    @abstractmethod
    def overview(self, symbol: str) -> CompanyOverview: ...

    @abstractmethod
    async def overview_async(self, symbol: str) -> CompanyOverview: ...

    def shareholders(self, symbol: str) -> list[Shareholder]:
        raise NotImplementedError

    async def shareholders_async(self, symbol: str) -> list[Shareholder]:
        raise NotImplementedError

    def officers(self, symbol: str) -> list[Officer]:
        raise NotImplementedError

    async def officers_async(self, symbol: str) -> list[Officer]:
        raise NotImplementedError

    def subsidiaries(self, symbol: str) -> list[Subsidiary]:
        raise NotImplementedError

    async def subsidiaries_async(self, symbol: str) -> list[Subsidiary]:
        raise NotImplementedError

    def events(self, symbol: str) -> list[CompanyEvent]:
        raise NotImplementedError

    async def events_async(self, symbol: str) -> list[CompanyEvent]:
        raise NotImplementedError

    def news(self, symbol: str) -> list[NewsItem]:
        raise NotImplementedError

    async def news_async(self, symbol: str) -> list[NewsItem]:
        raise NotImplementedError

    def ratio_summary(self, symbol: str) -> list[FinancialRow]:
        raise NotImplementedError

    async def ratio_summary_async(self, symbol: str) -> list[FinancialRow]:
        raise NotImplementedError


class FinanceProvider(ABC):
    """Interface every financial-report source (VCI, ...) must implement.

    All rows are returned in long format (`FinancialRow`) so different
    sources' wildly different report shapes (VCI flat, MAS parent/child, ...)
    can share one model — see [[KE-HOACH-CRAWL-DATA-CHI-TIET-1]] section 2.

    `note` (VCI thuyết minh BCTC) and `annual_plan` (MAS-only) are not part
    of the required contract since not every source has them.
    """

    @abstractmethod
    def balance_sheet(self, symbol: str, period: str = "quarter") -> list[FinancialRow]: ...

    @abstractmethod
    async def balance_sheet_async(
        self, symbol: str, period: str = "quarter"
    ) -> list[FinancialRow]: ...

    @abstractmethod
    def income_statement(self, symbol: str, period: str = "quarter") -> list[FinancialRow]: ...

    @abstractmethod
    async def income_statement_async(
        self, symbol: str, period: str = "quarter"
    ) -> list[FinancialRow]: ...

    @abstractmethod
    def cashflow(self, symbol: str, period: str = "quarter") -> list[FinancialRow]: ...

    @abstractmethod
    async def cashflow_async(self, symbol: str, period: str = "quarter") -> list[FinancialRow]: ...

    @abstractmethod
    def ratio(self, symbol: str, period: str = "quarter") -> list[FinancialRow]: ...

    @abstractmethod
    async def ratio_async(self, symbol: str, period: str = "quarter") -> list[FinancialRow]: ...

    def note(self, symbol: str, period: str = "quarter") -> list[FinancialRow]:
        raise NotImplementedError

    async def note_async(self, symbol: str, period: str = "quarter") -> list[FinancialRow]:
        raise NotImplementedError

    def annual_plan(self, symbol: str) -> list[FinancialRow]:
        raise NotImplementedError

    async def annual_plan_async(self, symbol: str) -> list[FinancialRow]:
        raise NotImplementedError
