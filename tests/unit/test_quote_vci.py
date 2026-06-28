import pytest
import respx
from httpx import Response

from samvnstock.providers.vci.const import QUOTE_HISTORY_URL
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
