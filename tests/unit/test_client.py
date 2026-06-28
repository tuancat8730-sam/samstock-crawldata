import time

import pytest
import respx
from httpx import Response

from samvnstock.core.client import HttpClient
from samvnstock.core.exceptions import RateLimitError, SourceError

_URL = "https://example.test/api/data"


@respx.mock
def test_get_retries_on_5xx_then_succeeds() -> None:
    route = respx.get(_URL)
    route.side_effect = [Response(503), Response(200, json={"ok": True})]

    result = HttpClient(backoff_factor=0).get(_URL)

    assert result == {"ok": True}
    assert route.call_count == 2


@respx.mock
def test_get_raises_rate_limit_error_after_retries_exhausted() -> None:
    respx.get(_URL).mock(return_value=Response(429))

    with pytest.raises(RateLimitError):
        HttpClient(max_retries=2, backoff_factor=0).get(_URL)


@respx.mock
def test_get_raises_source_error_on_4xx() -> None:
    respx.get(_URL).mock(return_value=Response(404))

    with pytest.raises(SourceError):
        HttpClient(backoff_factor=0).get(_URL)


@pytest.mark.asyncio
@respx.mock
async def test_aget_retries_on_5xx_then_succeeds() -> None:
    route = respx.get(_URL)
    route.side_effect = [Response(503), Response(200, json={"ok": True})]

    result = await HttpClient(backoff_factor=0).aget(_URL)

    assert result == {"ok": True}
    assert route.call_count == 2


@respx.mock
def test_rate_limiter_spaces_out_consecutive_requests() -> None:
    respx.get(_URL).mock(return_value=Response(200, json={"ok": True}))
    client = HttpClient(backoff_factor=0, requests_per_second=20)

    start = time.monotonic()
    client.get(_URL)
    client.get(_URL)
    elapsed = time.monotonic() - start

    assert elapsed >= 0.05
