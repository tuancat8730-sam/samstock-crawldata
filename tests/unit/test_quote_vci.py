import pytest
import respx
from httpx import Response

from samvnstock.providers.vci.const import QUOTE_HISTORY_URL, QUOTE_INTRADAY_URL
from samvnstock.providers.vci.quote import VciQuoteProvider

_RAW_RESPONSE = [
    {
        "t": [1704067200, 1704153600],
        "o": [10.0, 10.5],
        "h": [10.8, 11.0],
        "l": [9.9, 10.2],
        "c": [10.5, 10.8],
        "v": [100000, 120000],
    }
]


@respx.mock
def test_history_parses_ohlcv_bars() -> None:
    respx.post(QUOTE_HISTORY_URL).mock(return_value=Response(200, json=_RAW_RESPONSE))

    bars = VciQuoteProvider().history("VCB", start="2024-01-01", end="2024-01-02")

    assert len(bars) == 2
    assert bars[0].symbol == "VCB"
    assert bars[0].close == 10.5
    assert bars[1].volume == 120000


@respx.mock
def test_history_raises_source_error_on_empty_response() -> None:
    respx.post(QUOTE_HISTORY_URL).mock(return_value=Response(200, json=[]))

    with pytest.raises(Exception, match="Không tìm thấy dữ liệu"):
        VciQuoteProvider().history("VCB", start="2024-01-01", end="2024-01-02")


@pytest.mark.asyncio
@respx.mock
async def test_history_async_matches_sync_result() -> None:
    respx.post(QUOTE_HISTORY_URL).mock(return_value=Response(200, json=_RAW_RESPONSE))

    bars = await VciQuoteProvider().history_async("VCB", start="2024-01-01", end="2024-01-02")

    assert len(bars) == 2
    assert bars[0].open == 10.0


@respx.mock
def test_history_uses_one_minute_time_frame_for_1m_interval() -> None:
    route = respx.post(QUOTE_HISTORY_URL).mock(return_value=Response(200, json=_RAW_RESPONSE))

    VciQuoteProvider().history("VCB", start="2024-01-01", end="2024-01-02", interval="1m")

    import json

    payload = json.loads(route.calls[0].request.content)
    assert payload["timeFrame"] == "ONE_MINUTE"


def test_history_rejects_unsupported_interval() -> None:
    with pytest.raises(ValueError, match="không hỗ trợ trực tiếp"):
        VciQuoteProvider().history("VCB", start="2024-01-01", interval="5m")


@respx.mock
def test_history_drops_bars_with_invalid_ohlc() -> None:
    bad_response = [
        {
            "t": [1704067200, 1704153600],
            "o": [10.0, 10.5],
            "h": [10.8, 1.0],  # second bar: high < low, invalid
            "l": [9.9, 10.2],
            "c": [10.5, 10.8],
            "v": [100000, 120000],
        }
    ]
    respx.post(QUOTE_HISTORY_URL).mock(return_value=Response(200, json=bad_response))

    bars = VciQuoteProvider().history("VCB", start="2024-01-01", end="2024-01-02")

    assert len(bars) == 1


_INTRADAY_RESPONSE = {
    "data": [
        {"truncTime": 1704067200, "matchPrice": 10.5, "matchVol": 100, "matchType": "B"},
        {"truncTime": 1704067260, "matchPrice": 10.6, "matchVol": 200, "matchType": "S"},
    ]
}


@respx.mock
def test_intraday_parses_ticks() -> None:
    respx.post(QUOTE_INTRADAY_URL).mock(return_value=Response(200, json=_INTRADAY_RESPONSE))

    ticks = VciQuoteProvider().intraday("VCB")

    assert len(ticks) == 2
    assert ticks[0].price == 10.5
    assert ticks[1].match_type == "S"


@pytest.mark.asyncio
@respx.mock
async def test_intraday_async_matches_sync() -> None:
    respx.post(QUOTE_INTRADAY_URL).mock(return_value=Response(200, json=_INTRADAY_RESPONSE))

    ticks = await VciQuoteProvider().intraday_async("VCB")

    assert len(ticks) == 2
