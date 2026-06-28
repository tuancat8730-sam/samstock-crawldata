from typing import Any

from samvnstock.core.client import HttpClient
from samvnstock.core.exceptions import SourceError
from samvnstock.core.models import Industry, Symbol, SymbolIndustry
from samvnstock.core.normalize import normalize_keys
from samvnstock.providers.base import ListingProvider
from samvnstock.providers.vci.const import (
    GROUP_CODES,
    HEADERS,
    ICB_CODES_URL,
    LISTING_ALL_URL,
    LISTING_BY_GROUP_URL,
    SYMBOLS_BY_INDUSTRIES_URL,
)

_ICB_LEVELS = ("icbLv1", "icbLv2", "icbLv3", "icbLv4")


class VciListingProvider(ListingProvider):
    """Listing provider backed by VCI's `price/symbols/*` and `iq-insight-service` endpoints."""

    def __init__(self, client: HttpClient | None = None) -> None:
        self._client = client or HttpClient(headers=HEADERS)

    def all_symbols(self) -> list[Symbol]:
        data = self._client.get(LISTING_ALL_URL)
        return self._parse_symbols(data, stock_only=True)

    async def all_symbols_async(self) -> list[Symbol]:
        data = await self._client.aget(LISTING_ALL_URL)
        return self._parse_symbols(data, stock_only=True)

    def symbols_by_exchange(self) -> list[Symbol]:
        data = self._client.get(LISTING_ALL_URL)
        return self._parse_symbols(data, stock_only=False)

    async def symbols_by_exchange_async(self) -> list[Symbol]:
        data = await self._client.aget(LISTING_ALL_URL)
        return self._parse_symbols(data, stock_only=False)

    def symbols_by_group(self, group: str) -> list[str]:
        data = self._client.get(self._group_url(group))
        return self._parse_group(data)

    async def symbols_by_group_async(self, group: str) -> list[str]:
        data = await self._client.aget(self._group_url(group))
        return self._parse_group(data)

    def industry(self) -> list[Industry]:
        data = self._client.get(ICB_CODES_URL)
        return self._parse_industry(data)

    async def industry_async(self) -> list[Industry]:
        data = await self._client.aget(ICB_CODES_URL)
        return self._parse_industry(data)

    def symbols_by_industries(self) -> list[SymbolIndustry]:
        data = self._client.get(SYMBOLS_BY_INDUSTRIES_URL, params={"language": "1"})
        return self._parse_symbol_industries(data)

    async def symbols_by_industries_async(self) -> list[SymbolIndustry]:
        data = await self._client.aget(SYMBOLS_BY_INDUSTRIES_URL, params={"language": "1"})
        return self._parse_symbol_industries(data)

    def _group_url(self, group: str) -> str:
        code = GROUP_CODES.get(group.upper())
        if code is None:
            raise ValueError(
                f"Nhóm '{group}' không hợp lệ. Các giá trị hợp lệ: {sorted(GROUP_CODES)}"
            )
        return f"{LISTING_BY_GROUP_URL}?group={code}"

    def _parse_symbols(self, data: Any, stock_only: bool) -> list[Symbol]:
        if not isinstance(data, list):
            raise SourceError("VCI getAll trả về dữ liệu không hợp lệ")

        symbols: list[Symbol] = []
        for raw in data:
            record = normalize_keys(raw)
            if stock_only and record.get("type") != "STOCK":
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

    def _parse_group(self, data: Any) -> list[str]:
        if not isinstance(data, list):
            raise SourceError("VCI getByGroup trả về dữ liệu không hợp lệ")
        return [row["symbol"] for row in data if "symbol" in row]

    def _parse_industry(self, data: Any) -> list[Industry]:
        if not isinstance(data, dict) or not data.get("data"):
            raise SourceError("VCI icb-codes trả về dữ liệu không hợp lệ")

        return [
            Industry(
                icb_code=row["name"],
                icb_name=row["viSector"],
                en_icb_name=row.get("enSector"),
                level=row["icbLevel"],
            )
            for row in data["data"]
        ]

    def _parse_symbol_industries(self, data: Any) -> list[SymbolIndustry]:
        if not isinstance(data, dict) or data.get("data") is None:
            raise SourceError("VCI search-bar trả về dữ liệu không hợp lệ")

        rows: list[SymbolIndustry] = []
        for company in data["data"]:
            for level, key in enumerate(_ICB_LEVELS, start=1):
                icb = company.get(key)
                if not icb or not icb.get("code"):
                    continue
                rows.append(
                    SymbolIndustry(
                        symbol=company.get("code"),
                        organ_name=company.get("name"),
                        com_type_code=company.get("comTypeCode"),
                        icb_level=level,
                        icb_code=icb["code"],
                        icb_name=icb["name"],
                    )
                )
        return rows
