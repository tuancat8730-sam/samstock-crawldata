import asyncio
import time
from typing import Any

import httpx

from samvnstock.core.exceptions import RateLimitError, SourceError

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class _RateLimiter:
    """Simple fixed-interval rate limiter shared by sync and async call sites.

    Not thread-safe; each `HttpClient` instance is expected to be used from a
    single thread/coroutine at a time, matching how providers create clients.
    """

    def __init__(self, requests_per_second: float | None) -> None:
        self._min_interval = 1.0 / requests_per_second if requests_per_second else 0.0
        self._last_request_at: float | None = None

    def wait(self) -> None:
        delay = self._delay()
        if delay > 0:
            time.sleep(delay)
        self._last_request_at = time.monotonic()

    async def await_(self) -> None:
        delay = self._delay()
        if delay > 0:
            await asyncio.sleep(delay)
        self._last_request_at = time.monotonic()

    def _delay(self) -> float:
        if not self._min_interval or self._last_request_at is None:
            return 0.0
        elapsed = time.monotonic() - self._last_request_at
        return max(0.0, self._min_interval - elapsed)


class HttpClient:
    """Thin httpx wrapper with retry/backoff, shared by sync and async call sites.

    All network I/O for providers must go through this class so tests only
    need to mock one place (see [[development-workflow]] research-first rule:
    mirrors the request/response shape vnstock's `core/utils/client.py` uses,
    rewritten independently).
    """

    def __init__(
        self,
        headers: dict[str, str] | None = None,
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        requests_per_second: float | None = None,
    ) -> None:
        self._headers = headers or {}
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._rate_limiter = _RateLimiter(requests_per_second)

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code == 429:
            raise RateLimitError(f"Rate limited by {response.url}")
        if response.status_code >= 400:
            raise SourceError(f"{response.status_code} error from {response.url}")

    def _build_status_error(self, response: httpx.Response) -> Exception:
        if response.status_code == 429:
            return RateLimitError(f"Rate limited by {response.url}")
        return SourceError(f"{response.status_code} error from {response.url}")

    def get(self, url: str, params: dict[str, Any] | None = None) -> Any:
        with httpx.Client(headers=self._headers, timeout=self._timeout) as client:
            return self._request_with_retry(client.get, url, params=params)

    def post(self, url: str, json: dict[str, Any] | None = None) -> Any:
        with httpx.Client(headers=self._headers, timeout=self._timeout) as client:
            return self._request_with_retry(client.post, url, json=json)

    async def aget(self, url: str, params: dict[str, Any] | None = None) -> Any:
        async with httpx.AsyncClient(headers=self._headers, timeout=self._timeout) as client:
            return await self._arequest_with_retry(client.get, url, params=params)

    async def apost(self, url: str, json: dict[str, Any] | None = None) -> Any:
        async with httpx.AsyncClient(headers=self._headers, timeout=self._timeout) as client:
            return await self._arequest_with_retry(client.post, url, json=json)

    def _request_with_retry(self, method: Any, url: str, **kwargs: Any) -> Any:
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            self._rate_limiter.wait()
            try:
                response = method(url, **kwargs)
            except httpx.TransportError as exc:
                last_error = exc
            else:
                if response.status_code in _RETRYABLE_STATUS_CODES:
                    last_error = self._build_status_error(response)
                else:
                    self._raise_for_status(response)
                    return response.json()
            if attempt < self._max_retries - 1:
                time.sleep(self._backoff_factor * (2**attempt))
        raise last_error or SourceError(f"Request to {url} failed after retries")

    async def _arequest_with_retry(self, method: Any, url: str, **kwargs: Any) -> Any:
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            await self._rate_limiter.await_()
            try:
                response = await method(url, **kwargs)
            except httpx.TransportError as exc:
                last_error = exc
            else:
                if response.status_code in _RETRYABLE_STATUS_CODES:
                    last_error = self._build_status_error(response)
                else:
                    self._raise_for_status(response)
                    return response.json()
            if attempt < self._max_retries - 1:
                await asyncio.sleep(self._backoff_factor * (2**attempt))
        raise last_error or SourceError(f"Request to {url} failed after retries")
