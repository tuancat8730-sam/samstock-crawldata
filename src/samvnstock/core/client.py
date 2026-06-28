import asyncio
import time
from typing import Any

import httpx

from samvnstock.core.exceptions import RateLimitError, SourceError

_RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


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
    ) -> None:
        self._headers = headers or {}
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor

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
