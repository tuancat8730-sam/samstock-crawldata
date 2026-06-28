from abc import ABC, abstractmethod

from samvnstock.core.models import Bar, Symbol


class ListingProvider(ABC):
    """Interface every listing source (VCI, ...) must implement."""

    @abstractmethod
    def all_symbols(self) -> list[Symbol]: ...

    @abstractmethod
    async def all_symbols_async(self) -> list[Symbol]: ...


class QuoteProvider(ABC):
    """Interface every quote source (VCI, ...) must implement."""

    @abstractmethod
    def history(self, symbol: str, start: str, end: str | None = None) -> list[Bar]: ...

    @abstractmethod
    async def history_async(
        self, symbol: str, start: str, end: str | None = None
    ) -> list[Bar]: ...
