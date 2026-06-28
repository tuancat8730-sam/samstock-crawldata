import pytest
import respx
from httpx import Response

from samvnstock.providers.vnd.const import QUOTE_HISTORY_URL
from samvnstock.providers.vnd.quote import VndQuoteProvider

_RAW_RESPONSE = {
    "t": [1704067200, 1704153600],
    "o": [55.0, 55.4],
    "h": [55.5, 56.1],
    "l": [54.5, 54.9],
    "c": [55.4, 56.1],
    "v": [1785800, 1373000],
    "s": "ok",
}


@respx.mock
def test_history_parses_ohlcv_bars() -> None:
    respx.get(QUOTE_HISTORY_URL).mock(return_value=Response(200, json=_RAW_RESPONSE))

    bars = VndQuoteProvider().history("VCB", start="2024-01-01", end="2024-01-02")

    assert len(bars) == 2
    assert bars[0].symbol == "VCB"
    assert bars[1].close == 56.1


@respx.mock
def test_history_raises_source_error_when_status_not_ok() -> None:
    respx.get(QUOTE_HISTORY_URL).mock(return_value=Response(200, json={"s": "no_data"}))

    with pytest.raises(Exception, match="Không tìm thấy dữ liệu"):
        VndQuoteProvider().history("VCB", start="2024-01-01", end="2024-01-02")


@pytest.mark.asyncio
@respx.mock
async def test_history_async_matches_sync_result() -> None:
    respx.get(QUOTE_HISTORY_URL).mock(return_value=Response(200, json=_RAW_RESPONSE))

    bars = await VndQuoteProvider().history_async("VCB", start="2024-01-01", end="2024-01-02")

    assert len(bars) == 2
    assert bars[0].open == 55.0


@respx.mock
def test_facade_can_select_vnd_source() -> None:
    import samvnstock

    respx.get(QUOTE_HISTORY_URL).mock(return_value=Response(200, json=_RAW_RESPONSE))

    df = samvnstock.quote.history("VCB", start="2024-01-01", end="2024-01-02", source="vnd")

    assert df.iloc[0]["close"] == 55.4


@respx.mock
def test_history_passes_resolution_for_each_interval() -> None:
    route = respx.get(QUOTE_HISTORY_URL).mock(return_value=Response(200, json=_RAW_RESPONSE))

    VndQuoteProvider().history("VCB", start="2024-01-01", interval="15m")

    assert route.calls[0].request.url.params["resolution"] == "15"


def test_history_rejects_unsupported_interval() -> None:
    with pytest.raises(ValueError, match="không hỗ trợ interval"):
        VndQuoteProvider().history("VCB", start="2024-01-01", interval="2H")
