from typing import Any

from samvnstock.core.client import HttpClient
from samvnstock.core.exceptions import SourceError
from samvnstock.core.models import FinancialRow
from samvnstock.core.normalize import to_float
from samvnstock.providers._shared.finance_items import VCI_RATIO_ITEM_MAP
from samvnstock.providers.base import FinanceProvider
from samvnstock.providers.vci.const import FINANCE_SECTION_MAP, HEADERS, VCI_COMPANY_URL

_YEAR_KEYS = ("year", "yearReport")
_QUARTER_KEYS = ("quarter", "lengthReport")
# Metadata fields present on each report row that are never financial items.
_METADATA_FIELDS = {"year", "yearReport", "quarter", "lengthReport", "report_period"}


def _first_value(raw: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if raw.get(key) is not None:
            return raw[key]
    return None


def _period_label(raw: dict[str, Any], period: str) -> str:
    year = _first_value(raw, _YEAR_KEYS)
    if year is None:
        return "N/A"
    quarter = _first_value(raw, _QUARTER_KEYS)
    if period == "quarter" and quarter is not None and int(quarter) < 5:
        return f"{int(year)}-Q{int(quarter)}"
    return str(int(year))


class VciFinanceProvider(FinanceProvider):
    """Financial report provider backed by VCI's `financial-statement` and
    `statistics-financial` endpoints.

    Item names/parent codes for balance sheet, income statement, and cashflow
    come from VCI's own `financial-statement/metrics` endpoint (which already
    encodes a parent/child hierarchy, not just MAS as originally assumed in
    [[KE-HOACH-CRAWL-DATA-CHI-TIET-1]]). `ratio` uses a small hand-curated
    item-code map (`providers/_shared/finance_items.py`) since VCI's ratio
    fields are flat, known keys rather than metrics-driven.
    """

    def __init__(self, client: HttpClient | None = None) -> None:
        self._client = client or HttpClient(headers=HEADERS)

    def balance_sheet(self, symbol: str, period: str = "quarter") -> list[FinancialRow]:
        return self._report(symbol, "balance_sheet", period)

    async def balance_sheet_async(
        self, symbol: str, period: str = "quarter"
    ) -> list[FinancialRow]:
        return await self._report_async(symbol, "balance_sheet", period)

    def income_statement(self, symbol: str, period: str = "quarter") -> list[FinancialRow]:
        return self._report(symbol, "income_statement", period)

    async def income_statement_async(
        self, symbol: str, period: str = "quarter"
    ) -> list[FinancialRow]:
        return await self._report_async(symbol, "income_statement", period)

    def cashflow(self, symbol: str, period: str = "quarter") -> list[FinancialRow]:
        return self._report(symbol, "cashflow", period)

    async def cashflow_async(self, symbol: str, period: str = "quarter") -> list[FinancialRow]:
        return await self._report_async(symbol, "cashflow", period)

    def ratio(self, symbol: str, period: str = "quarter") -> list[FinancialRow]:
        data = self._client.get(f"{VCI_COMPANY_URL}/{symbol}/statistics-financial")
        return self._parse_ratio(data, symbol, period)

    async def ratio_async(self, symbol: str, period: str = "quarter") -> list[FinancialRow]:
        data = await self._client.aget(f"{VCI_COMPANY_URL}/{symbol}/statistics-financial")
        return self._parse_ratio(data, symbol, period)

    def _report(self, symbol: str, statement: str, period: str) -> list[FinancialRow]:
        section = self._section(statement)
        raw = self._client.get(
            f"{VCI_COMPANY_URL}/{symbol}/financial-statement", params={"section": section}
        )
        metrics = self._client.get(f"{VCI_COMPANY_URL}/{symbol}/financial-statement/metrics")
        item_map = self._build_item_map(metrics, symbol)
        return self._parse_report(raw, item_map, symbol, statement, period)

    async def _report_async(self, symbol: str, statement: str, period: str) -> list[FinancialRow]:
        section = self._section(statement)
        raw = await self._client.aget(
            f"{VCI_COMPANY_URL}/{symbol}/financial-statement", params={"section": section}
        )
        metrics = await self._client.aget(f"{VCI_COMPANY_URL}/{symbol}/financial-statement/metrics")
        item_map = self._build_item_map(metrics, symbol)
        return self._parse_report(raw, item_map, symbol, statement, period)

    def _section(self, statement: str) -> str:
        section = FINANCE_SECTION_MAP.get(statement)
        if section is None:
            raise ValueError(f"Loại báo cáo không hợp lệ: {statement}")
        return section

    def _build_item_map(self, data: Any, symbol: str) -> dict[str, tuple[str, str | None]]:
        payload = data.get("data") if isinstance(data, dict) else None
        if not payload:
            raise SourceError(f"Không tìm thấy metadata chỉ tiêu BCTC cho {symbol}")

        item_map: dict[str, tuple[str, str | None]] = {}
        for items in payload.values():
            for item in items:
                field = item.get("field")
                if not field:
                    continue
                name = item.get("titleVi") or item.get("titleEn") or field
                item_map[field] = (name, item.get("parent"))
        return item_map

    def _parse_report(
        self,
        data: Any,
        item_map: dict[str, tuple[str, str | None]],
        symbol: str,
        statement: str,
        period: str,
    ) -> list[FinancialRow]:
        payload = data.get("data") if isinstance(data, dict) else None
        if payload is None:
            raise SourceError(f"Không tìm thấy báo cáo {statement} cho {symbol}")

        target_key = "years" if period == "year" else "quarters"
        rows = payload.get(target_key) or []

        result = []
        for raw in rows:
            period_label = _period_label(raw, period)
            for field, value in raw.items():
                if field in _METADATA_FIELDS or field not in item_map:
                    continue
                try:
                    parsed_value = to_float(value)
                except ValueError:
                    continue
                name, parent = item_map[field]
                result.append(
                    FinancialRow(
                        symbol=symbol,
                        statement=statement,
                        period=period_label,
                        item_code=field,
                        item_name=name,
                        value=parsed_value,
                        parent_code=parent,
                    )
                )
        return result

    def _parse_ratio(self, data: Any, symbol: str, period: str) -> list[FinancialRow]:
        payload = data.get("data") if isinstance(data, dict) else None
        if payload is None:
            raise SourceError(f"Không tìm thấy chỉ số tài chính cho {symbol}")

        rows = payload if isinstance(payload, list) else [payload]
        result = []
        for raw in rows:
            period_label = _period_label(raw, period)
            for key, value in raw.items():
                if key not in VCI_RATIO_ITEM_MAP:
                    continue
                item_code, item_name = VCI_RATIO_ITEM_MAP[key]
                try:
                    parsed_value = to_float(value)
                except ValueError:
                    continue
                result.append(
                    FinancialRow(
                        symbol=symbol,
                        statement="ratio",
                        period=period_label,
                        item_code=item_code,
                        item_name=item_name,
                        value=parsed_value,
                        unit=None,
                    )
                )
        return result
