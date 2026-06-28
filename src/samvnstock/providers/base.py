from abc import ABC, abstractmethod

from samvnstock.core.models import Bar, Industry, Symbol, SymbolIndustry, Tick


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
