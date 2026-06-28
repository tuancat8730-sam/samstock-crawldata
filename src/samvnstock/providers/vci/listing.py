from typing import Any

from samvnstock.core.client import HttpClient
from samvnstock.core.exceptions import SourceError
from samvnstock.core.models import Symbol
from samvnstock.core.normalize import normalize_keys
from samvnstock.providers.base import ListingProvider
from samvnstock.providers.vci.const import HEADERS, LISTING_ALL_URL


class VciListingProvider(ListingProvider):
    """Listing provider backed by VCI's `price/symbols/getAll` endpoint."""

    def __init__(self, client: HttpClient | None = None) -> None:
        self._client = client or HttpClient(headers=HEADERS)

    def all_symbols(self) -> list[Symbol]:
        data = self._client.get(LISTING_ALL_URL)
        return self._parse(data)

    async def all_symbols_async(self) -> list[Symbol]:
        data = await self._client.aget(LISTING_ALL_URL)
        return self._parse(data)

    def _parse(self, data: Any) -> list[Symbol]:
        if not isinstance(data, list):
            raise SourceError("VCI getAll trả về dữ liệu không hợp lệ")

        symbols: list[Symbol] = []
        for raw in data:
            record = normalize_keys(raw)
            if record.get("type") != "STOCK":
                continue
            symbols.append(
                Symbol(
                    symbol=record["symbol"],
                    exchange=record.get("board", ""),
                    organ_name=record.get("organ_name"),
                    type=record.get("type"),
                )
            )
        return symbols
