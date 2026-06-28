import pytest
import respx
from httpx import Response

import samvnstock
from samvnstock.providers.vci.const import QUOTE_HISTORY_URL as VCI_URL
from samvnstock.providers.vnd.const import QUOTE_HISTORY_URL as VND_URL

_VND_RESPONSE = {
    "t": [1704067200],
    "o": [55.0],
    "h": [55.5],
    "l": [54.5],
    "c": [55.4],
    "v": [1785800],
    "s": "ok",
}


@respx.mock
def test_auto_source_falls_back_to_vnd_when_vci_fails() -> None:
    respx.post(VCI_URL).mock(return_value=Response(500))
    respx.get(VND_URL).mock(return_value=Response(200, json=_VND_RESPONSE))

    df = samvnstock.quote.history("VCB", start="2024-01-01", source="auto")

    assert df.iloc[0]["close"] == 55.4


@respx.mock
def test_auto_source_uses_vci_when_it_succeeds() -> None:
    vci_response = [
        {"t": [1704067200], "o": [10.0], "h": [10.8], "l": [9.9], "c": [10.5], "v": [100000]}
    ]
    respx.post(VCI_URL).mock(return_value=Response(200, json=vci_response))

    df = samvnstock.quote.history("VCB", start="2024-01-01", source="auto")

    assert df.iloc[0]["close"] == 10.5


@pytest.mark.asyncio
@respx.mock
async def test_auto_source_async_falls_back_to_vnd() -> None:
    respx.post(VCI_URL).mock(return_value=Response(500))
    respx.get(VND_URL).mock(return_value=Response(200, json=_VND_RESPONSE))

    df = await samvnstock.quote.history_async("VCB", start="2024-01-01", source="auto")

    assert df.iloc[0]["close"] == 55.4
