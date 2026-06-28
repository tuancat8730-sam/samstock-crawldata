import pytest
import respx
from httpx import Response

from samvnstock.providers.vci.const import (
    ICB_CODES_URL,
    LISTING_ALL_URL,
    LISTING_BY_GROUP_URL,
    SYMBOLS_BY_INDUSTRIES_URL,
)
from samvnstock.providers.vci.listing import VciListingProvider

_ALL_SYMBOLS_RESPONSE = [
    {"symbol": "VCB", "board": "HOSE", "type": "STOCK", "organName": "Vietcombank"},
    {"symbol": "VN30F2509", "board": "DER", "type": "FUTURE", "organName": "VN30F2509"},
]

_ICB_RESPONSE = {
    "data": [
        {"name": "8300", "viSector": "Ngân hàng", "enSector": "Banks", "icbLevel": 3},
    ]
}

_SEARCH_BAR_RESPONSE = {
    "data": [
        {
            "code": "VCB",
            "name": "Vietcombank",
            "comTypeCode": "NH",
            "icbLv1": {"code": "8000", "name": "Tài chính"},
            "icbLv2": {"code": "8300", "name": "Ngân hàng"},
            "icbLv3": None,
            "icbLv4": None,
        }
    ]
}

_GROUP_RESPONSE = [{"symbol": "VCB"}, {"symbol": "BID"}]


@respx.mock
def test_symbols_by_exchange_keeps_non_stock_types() -> None:
    respx.get(LISTING_ALL_URL).mock(return_value=Response(200, json=_ALL_SYMBOLS_RESPONSE))

    symbols = VciListingProvider().symbols_by_exchange()

    assert len(symbols) == 2
    assert {s.symbol for s in symbols} == {"VCB", "VN30F2509"}


@pytest.mark.asyncio
@respx.mock
async def test_symbols_by_exchange_async_matches_sync() -> None:
    respx.get(LISTING_ALL_URL).mock(return_value=Response(200, json=_ALL_SYMBOLS_RESPONSE))

    symbols = await VciListingProvider().symbols_by_exchange_async()

    assert len(symbols) == 2


@respx.mock
def test_symbols_by_group_returns_symbol_list() -> None:
    respx.get(url__regex=rf"{LISTING_BY_GROUP_URL}.*").mock(
        return_value=Response(200, json=_GROUP_RESPONSE)
    )

    symbols = VciListingProvider().symbols_by_group("VN30")

    assert symbols == ["VCB", "BID"]


def test_symbols_by_group_rejects_unknown_group() -> None:
    with pytest.raises(ValueError, match="không hợp lệ"):
        VciListingProvider().symbols_by_group("NOT-A-GROUP")


@respx.mock
def test_industry_parses_icb_codes() -> None:
    respx.get(ICB_CODES_URL).mock(return_value=Response(200, json=_ICB_RESPONSE))

    rows = VciListingProvider().industry()

    assert len(rows) == 1
    assert rows[0].icb_code == "8300"
    assert rows[0].icb_name == "Ngân hàng"
    assert rows[0].level == 3


@respx.mock
def test_symbols_by_industries_flattens_icb_levels() -> None:
    respx.get(url__regex=rf"{SYMBOLS_BY_INDUSTRIES_URL}.*").mock(
        return_value=Response(200, json=_SEARCH_BAR_RESPONSE)
    )

    rows = VciListingProvider().symbols_by_industries()

    assert len(rows) == 2
    assert rows[0].symbol == "VCB"
    assert rows[0].icb_level == 1
    assert rows[1].icb_level == 2
    assert rows[1].icb_code == "8300"


@pytest.mark.asyncio
@respx.mock
async def test_symbols_by_group_async_matches_sync() -> None:
    respx.get(url__regex=rf"{LISTING_BY_GROUP_URL}.*").mock(
        return_value=Response(200, json=_GROUP_RESPONSE)
    )

    symbols = await VciListingProvider().symbols_by_group_async("VN30")

    assert symbols == ["VCB", "BID"]


@pytest.mark.asyncio
@respx.mock
async def test_industry_async_matches_sync() -> None:
    respx.get(ICB_CODES_URL).mock(return_value=Response(200, json=_ICB_RESPONSE))

    rows = await VciListingProvider().industry_async()

    assert len(rows) == 1


@pytest.mark.asyncio
@respx.mock
async def test_symbols_by_industries_async_matches_sync() -> None:
    respx.get(url__regex=rf"{SYMBOLS_BY_INDUSTRIES_URL}.*").mock(
        return_value=Response(200, json=_SEARCH_BAR_RESPONSE)
    )

    rows = await VciListingProvider().symbols_by_industries_async()

    assert len(rows) == 2
