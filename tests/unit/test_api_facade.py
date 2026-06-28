import pytest
import respx
from httpx import Response

import samvnstock
from samvnstock.providers.vci.const import LISTING_ALL_URL, QUOTE_HISTORY_URL


@respx.mock
def test_listing_all_symbols_returns_dataframe() -> None:
    raw = {"symbol": "VCB", "board": "HOSE", "type": "STOCK", "organName": "Vietcombank"}
    respx.get(LISTING_ALL_URL).mock(return_value=Response(200, json=[raw]))

    df = samvnstock.listing.all_symbols()

    assert list(df.columns) == ["symbol", "exchange", "organ_name", "type"]
    assert df.iloc[0]["symbol"] == "VCB"


@respx.mock
def test_quote_history_returns_dataframe() -> None:
    raw = {"t": [1704067200], "o": [10.0], "h": [10.8], "l": [9.9], "c": [10.5], "v": [100000]}
    respx.post(QUOTE_HISTORY_URL).mock(return_value=Response(200, json=[raw]))

    df = samvnstock.quote.history("VCB", start="2024-01-01", end="2024-01-01")

    assert list(df.columns) == ["symbol", "time", "open", "high", "low", "close", "volume"]
    assert df.iloc[0]["close"] == 10.5


def test_unknown_source_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Không có provider"):
        samvnstock.listing.all_symbols(source="not-a-real-source")


@respx.mock
async def test_listing_all_symbols_async_returns_dataframe() -> None:
    raw = {"symbol": "VCB", "board": "HOSE", "type": "STOCK", "organName": "Vietcombank"}
    respx.get(LISTING_ALL_URL).mock(return_value=Response(200, json=[raw]))

    df = await samvnstock.listing.all_symbols_async()

    assert df.iloc[0]["symbol"] == "VCB"


@respx.mock
async def test_quote_history_async_returns_dataframe() -> None:
    raw = {"t": [1704067200], "o": [10.0], "h": [10.8], "l": [9.9], "c": [10.5], "v": [100000]}
    respx.post(QUOTE_HISTORY_URL).mock(return_value=Response(200, json=[raw]))

    df = await samvnstock.quote.history_async("VCB", start="2024-01-01", end="2024-01-01")

    assert df.iloc[0]["close"] == 10.5
