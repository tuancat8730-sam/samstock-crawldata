import pytest

from samvnstock.api._fallback import with_fallback, with_fallback_async
from samvnstock.core.exceptions import SourceError, SourceUnavailableError


def test_with_fallback_returns_first_success() -> None:
    def fetch(symbol: str, source: str) -> str:
        if source == "vci":
            raise SourceError("vci down")
        return f"{symbol}-{source}"

    result = with_fallback(fetch, ["vci", "vnd"], "VCB")

    assert result == "VCB-vnd"


def test_with_fallback_raises_when_all_sources_fail() -> None:
    def fetch(symbol: str, source: str) -> str:
        raise SourceError(f"{source} down")

    with pytest.raises(SourceUnavailableError):
        with_fallback(fetch, ["vci", "vnd"], "VCB")


def test_with_fallback_does_not_swallow_non_source_errors() -> None:
    def fetch(symbol: str, source: str) -> str:
        raise TypeError("boom")

    with pytest.raises(TypeError):
        with_fallback(fetch, ["vci", "vnd"], "VCB")


@pytest.mark.asyncio
async def test_with_fallback_async_returns_first_success() -> None:
    async def fetch(symbol: str, source: str) -> str:
        if source == "vci":
            raise SourceError("vci down")
        return f"{symbol}-{source}"

    result = await with_fallback_async(fetch, ["vci", "vnd"], "VCB")

    assert result == "VCB-vnd"


@pytest.mark.asyncio
async def test_with_fallback_async_raises_when_all_sources_fail() -> None:
    async def fetch(symbol: str, source: str) -> str:
        raise SourceError(f"{source} down")

    with pytest.raises(SourceUnavailableError):
        await with_fallback_async(fetch, ["vci", "vnd"], "VCB")
