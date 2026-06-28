from datetime import datetime, timedelta
from typing import Any

from samvnstock.core.client import HttpClient
from samvnstock.core.exceptions import SourceError
from samvnstock.core.models import (
    CompanyEvent,
    CompanyOverview,
    FinancialRow,
    NewsItem,
    Officer,
    Shareholder,
    Subsidiary,
)
from samvnstock.core.normalize import remap, to_float, to_int
from samvnstock.providers.base import CompanyProvider
from samvnstock.providers.vci.const import (
    COMPANY_EVENTS_URL,
    COMPANY_NEWS_URL,
    HEADERS,
    VCI_COMPANY_URL,
)
from samvnstock.utils.datetime import to_yyyymmdd

_OVERVIEW_FIELD_MAP = {
    "ticker": "symbol",
    "viOrganName": "organ_name",
    "viOrganShortName": "organ_short_name",
    "sectorVn": "sector",
    "profile": "company_profile",
    "listingDate": "listing_date",
    "numberOfSharesMktCap": "issue_share",
}

_SHAREHOLDER_FIELD_MAP = {
    "ownerName": "share_holder",
    "quantity": "quantity",
    "percentage": "share_own_percent",
    "updateDate": "update_date",
}

_OFFICER_FIELD_MAP = {
    "ownerName": "officer_name",
    "positionName": "officer_position",
    "percentage": "officer_own_percent",
    "quantity": "officer_own_quantity",
}

_RELATIONSHIP_FIELD_MAP = {
    "rightOrganNameVi": "organ_name",
    "rightOrganCode": "sub_organ_code",
    "ownedPercentage": "ownership_percent",
}

# Events/news payload shapes are not fully documented even in vnstock's own
# source (it generically renames camelCase -> snake_case and only drops a
# known set of columns). These candidate keys are a best effort; report a
# mismatch if VCI's real response uses different field names.
_EVENT_TITLE_KEYS = ("eventTitle", "eventListName", "name", "title")
_EVENT_CODE_KEYS = ("eventCode", "eventListCode", "code")
_NEWS_TITLE_KEYS = ("title", "newsTitle", "headline")


def _first_present(raw: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if raw.get(key) is not None:
            return raw[key]
    return None


def _normalize_update_date(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000).strftime("%Y-%m-%d")
    return str(value)


class VciCompanyProvider(CompanyProvider):
    """Company profile provider backed by VCI's `iq-insight-service/v1/company` endpoints."""

    def __init__(self, client: HttpClient | None = None) -> None:
        self._client = client or HttpClient(headers=HEADERS)

    def overview(self, symbol: str) -> CompanyOverview:
        data = self._client.get(f"{VCI_COMPANY_URL}/details", params={"ticker": symbol})
        return self._parse_overview(data, symbol)

    async def overview_async(self, symbol: str) -> CompanyOverview:
        data = await self._client.aget(f"{VCI_COMPANY_URL}/details", params={"ticker": symbol})
        return self._parse_overview(data, symbol)

    def shareholders(self, symbol: str) -> list[Shareholder]:
        data = self._client.get(f"{VCI_COMPANY_URL}/{symbol}/shareholder")
        return self._parse_shareholders(data, symbol)

    async def shareholders_async(self, symbol: str) -> list[Shareholder]:
        data = await self._client.aget(f"{VCI_COMPANY_URL}/{symbol}/shareholder")
        return self._parse_shareholders(data, symbol)

    def officers(self, symbol: str) -> list[Officer]:
        data = self._client.get(f"{VCI_COMPANY_URL}/{symbol}/shareholder")
        return self._parse_officers(data, symbol)

    async def officers_async(self, symbol: str) -> list[Officer]:
        data = await self._client.aget(f"{VCI_COMPANY_URL}/{symbol}/shareholder")
        return self._parse_officers(data, symbol)

    def subsidiaries(self, symbol: str) -> list[Subsidiary]:
        data = self._client.get(f"{VCI_COMPANY_URL}/{symbol}/relationship")
        return self._parse_subsidiaries(data, symbol)

    async def subsidiaries_async(self, symbol: str) -> list[Subsidiary]:
        data = await self._client.aget(f"{VCI_COMPANY_URL}/{symbol}/relationship")
        return self._parse_subsidiaries(data, symbol)

    def events(self, symbol: str) -> list[CompanyEvent]:
        data = self._client.get(COMPANY_EVENTS_URL, params=self._event_params(symbol))
        return self._parse_events(data, symbol)

    async def events_async(self, symbol: str) -> list[CompanyEvent]:
        data = await self._client.aget(COMPANY_EVENTS_URL, params=self._event_params(symbol))
        return self._parse_events(data, symbol)

    def news(self, symbol: str) -> list[NewsItem]:
        data = self._client.get(COMPANY_NEWS_URL, params=self._news_params(symbol))
        return self._parse_news(data, symbol)

    async def news_async(self, symbol: str) -> list[NewsItem]:
        data = await self._client.aget(COMPANY_NEWS_URL, params=self._news_params(symbol))
        return self._parse_news(data, symbol)

    def ratio_summary(self, symbol: str) -> list[FinancialRow]:
        data = self._client.get(f"{VCI_COMPANY_URL}/{symbol}/statistics-financial")
        return self._parse_ratio_summary(data, symbol)

    async def ratio_summary_async(self, symbol: str) -> list[FinancialRow]:
        data = await self._client.aget(f"{VCI_COMPANY_URL}/{symbol}/statistics-financial")
        return self._parse_ratio_summary(data, symbol)

    def _event_params(self, symbol: str) -> dict[str, Any]:
        now = datetime.now()
        return {
            "ticker": symbol,
            "fromDate": to_yyyymmdd(now - timedelta(days=365 * 10)),
            "toDate": to_yyyymmdd(now),
            "eventCode": "DIV,ISS,DDIND,DDINS,DDRP,AGME,AGMR,EGME,AIS,MA,MOVE,NLIS,OTHE,RETU,SUSP",
            "page": 0,
            "size": 50,
        }

    def _news_params(self, symbol: str) -> dict[str, Any]:
        now = datetime.now()
        return {
            "ticker": symbol,
            "fromDate": to_yyyymmdd(now - timedelta(days=365 * 10)),
            "toDate": to_yyyymmdd(now),
            "languageId": 1,
            "page": 0,
            "size": 50,
        }

    def _parse_overview(self, data: Any, symbol: str) -> CompanyOverview:
        payload = data.get("data") if isinstance(data, dict) else None
        if not payload:
            raise SourceError(f"Không tìm thấy thông tin tổng quan cho {symbol}")

        row = remap(payload, _OVERVIEW_FIELD_MAP)
        row["issue_share"] = to_int(row.get("issue_share"))
        row.setdefault("symbol", symbol)
        return CompanyOverview(**row)

    def _parse_shareholders(self, data: Any, symbol: str) -> list[Shareholder]:
        rows = self._extract_list(data)
        shareholders = []
        for raw in rows:
            row = remap(raw, _SHAREHOLDER_FIELD_MAP)
            if "share_holder" not in row:
                continue
            shareholders.append(
                Shareholder(
                    symbol=symbol,
                    share_holder=row["share_holder"],
                    quantity=to_int(row.get("quantity")),
                    share_own_percent=to_float(row.get("share_own_percent")),
                    update_date=_normalize_update_date(row.get("update_date")),
                )
            )
        return shareholders

    def _parse_officers(self, data: Any, symbol: str) -> list[Officer]:
        rows = self._extract_list(data)
        officers = []
        for raw in rows:
            if raw.get("ownerType") != "INDIVIDUAL" or not raw.get("positionName"):
                continue
            row = remap(raw, _OFFICER_FIELD_MAP)
            officers.append(
                Officer(
                    symbol=symbol,
                    officer_name=row["officer_name"],
                    officer_position=row.get("officer_position"),
                    officer_own_percent=to_float(row.get("officer_own_percent")),
                    officer_own_quantity=to_int(row.get("officer_own_quantity")),
                )
            )
        return officers

    def _parse_subsidiaries(self, data: Any, symbol: str) -> list[Subsidiary]:
        payload = data.get("data") if isinstance(data, dict) else None
        if not isinstance(payload, dict):
            raise SourceError(f"Không tìm thấy thông tin công ty con cho {symbol}")

        result = []
        for kind, raw_list in (
            ("subsidiary", payload.get("subsidiaries") or []),
            ("affiliate", payload.get("affiliates") or []),
        ):
            for raw in raw_list:
                row = remap(raw, _RELATIONSHIP_FIELD_MAP)
                if "organ_name" not in row:
                    continue
                result.append(
                    Subsidiary(
                        symbol=symbol,
                        organ_name=row["organ_name"],
                        ownership_percent=to_float(row.get("ownership_percent")),
                        sub_organ_code=row.get("sub_organ_code"),
                        type=kind,
                    )
                )
        return result

    def _parse_events(self, data: Any, symbol: str) -> list[CompanyEvent]:
        rows = self._extract_paginated(data)
        events = []
        for raw in rows:
            events.append(
                CompanyEvent(
                    symbol=symbol,
                    event_title=_first_present(raw, _EVENT_TITLE_KEYS),
                    event_code=_first_present(raw, _EVENT_CODE_KEYS),
                    public_date=raw.get("publicDate"),
                    record_date=raw.get("recordDate"),
                    exright_date=raw.get("exrightDate"),
                )
            )
        return events

    def _parse_news(self, data: Any, symbol: str) -> list[NewsItem]:
        rows = self._extract_paginated(data)
        news = []
        for raw in rows:
            title = _first_present(raw, _NEWS_TITLE_KEYS)
            if title is None:
                continue
            news.append(
                NewsItem(
                    symbol=symbol,
                    title=title,
                    public_date=raw.get("publicDate"),
                    source=raw.get("newsSource") or raw.get("source"),
                )
            )
        return news

    def _parse_ratio_summary(self, data: Any, symbol: str) -> list[FinancialRow]:
        payload = data.get("data") if isinstance(data, dict) else None
        if payload is None:
            raise SourceError(f"Không tìm thấy chỉ số tài chính cho {symbol}")

        rows = payload if isinstance(payload, list) else [payload]
        result = []
        for raw in rows:
            for item_name, value in raw.items():
                if item_name in ("__typename", "ticker"):
                    continue
                try:
                    parsed_value = to_float(value)
                except ValueError:
                    continue
                if parsed_value is None and not isinstance(value, (int, float)):
                    continue
                result.append(
                    FinancialRow(
                        symbol=symbol,
                        statement="ratio_summary",
                        item_name=item_name,
                        value=parsed_value,
                        unit=None,
                    )
                )
        return result

    def _extract_list(self, data: Any) -> list[dict[str, Any]]:
        payload = data.get("data") if isinstance(data, dict) else data
        return payload if isinstance(payload, list) else []

    def _extract_paginated(self, data: Any) -> list[dict[str, Any]]:
        payload = data.get("data") if isinstance(data, dict) else None
        if isinstance(payload, dict):
            return payload.get("content") or []
        return payload if isinstance(payload, list) else []
