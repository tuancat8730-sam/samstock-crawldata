import pandas as pd

import samvnstock.providers.vci  # noqa: F401  (registers the "vci" provider)
from samvnstock.core.registry import ProviderRegistry
from samvnstock.providers.base import QuoteProvider


def _provider(source: str) -> QuoteProvider:
    provider_cls = ProviderRegistry.get("quote", source)
    return provider_cls()  # type: ignore[no-any-return]


def history(symbol: str, start: str, end: str | None = None, source: str = "vci") -> pd.DataFrame:
    """Lịch sử giá OHLCV theo ngày cho một mã chứng khoán."""
    bars = _provider(source).history(symbol, start, end)
    return pd.DataFrame([b.model_dump() for b in bars])


async def history_async(
    symbol: str, start: str, end: str | None = None, source: str = "vci"
) -> pd.DataFrame:
    bars = await _provider(source).history_async(symbol, start, end)
    return pd.DataFrame([b.model_dump() for b in bars])
