import pytest
import respx
from httpx import Response

from samvnstock.providers.vci.const import LISTING_ALL_URL
from samvnstock.providers.vci.listing import VciListingProvider

_RAW_RESPONSE = [
    {"symbol": "VCB", "board": "HOSE", "type": "STOCK", "organName": "Vietcombank"},
    {"symbol": "VN30F2509", "board": "DER", "type": "FUTURE", "organName": "VN30F2509"},
]


@respx.mock
def test_all_symbols_filters_stock_only_and_normalizes_fields() -> None:
    respx.get(LISTING_ALL_URL).mock(return_value=Response(200, json=_RAW_RESPONSE))

    symbols = VciListingProvider().all_symbols()

    assert len(symbols) == 1
    assert symbols[0].symbol == "VCB"
    assert symbols[0].exchange == "HOSE"
    assert symbols[0].organ_name == "Vietcombank"


@pytest.mark.asyncio
@respx.mock
async def test_all_symbols_async_matches_sync_result() -> None:
    respx.get(LISTING_ALL_URL).mock(return_value=Response(200, json=_RAW_RESPONSE))

    symbols = await VciListingProvider().all_symbols_async()

    assert len(symbols) == 1
    assert symbols[0].symbol == "VCB"
