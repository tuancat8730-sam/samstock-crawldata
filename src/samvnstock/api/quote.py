from collections.abc import Sequence

import pandas as pd
from pydantic import BaseModel

import samvnstock.providers.vci  # noqa: F401  (registers the "vci" provider)
import samvnstock.providers.vnd  # noqa: F401  (registers the "vnd" provider)
from samvnstock.api._fallback import with_fallback, with_fallback_async
from samvnstock.core.registry import ProviderRegistry
from samvnstock.providers.base import QuoteProvider

_FALLBACK_SOURCES = ["vci", "vnd"]


def _provider(source: str) -> QuoteProvider:
    provider_cls = ProviderRegistry.get("quote", source)
    return provider_cls()  # type: ignore[no-any-return]


def _to_df(models: Sequence[BaseModel]) -> pd.DataFrame:
    return pd.DataFrame([m.model_dump() for m in models])


def _history_single(
    symbol: str, start: str, end: str | None, interval: str, source: str
) -> pd.DataFrame:
    return _to_df(_provider(source).history(symbol, start, end, interval))


async def _history_single_async(
    symbol: str, start: str, end: str | None, interval: str, source: str
) -> pd.DataFrame:
    return _to_df(await _provider(source).history_async(symbol, start, end, interval))


def history(
    symbol: str,
    start: str,
    end: str | None = None,
    interval: str = "1D",
    source: str = "vci",
) -> pd.DataFrame:
    """Lịch sử giá OHLCV cho một mã chứng khoán.

    - `source="vci"` (mặc định): hỗ trợ interval "1D", "1H", "1m".
    - `source="vnd"`: dự phòng, hỗ trợ thêm "5m", "15m", "30m".
    - `source="auto"`: thử "vci" trước, nếu lỗi tự chuyển sang "vnd"
      (xem `api/_fallback.py`).
    """
    if source == "auto":
        return with_fallback(
            _history_single, _FALLBACK_SOURCES, symbol, start, end=end, interval=interval
        )
    return _history_single(symbol, start, end, interval, source)


async def history_async(
    symbol: str,
    start: str,
    end: str | None = None,
    interval: str = "1D",
    source: str = "vci",
) -> pd.DataFrame:
    if source == "auto":
        return await with_fallback_async(
            _history_single_async, _FALLBACK_SOURCES, symbol, start, end=end, interval=interval
        )
    return await _history_single_async(symbol, start, end, interval, source)


def intraday(symbol: str, page_size: int = 100, source: str = "vci") -> pd.DataFrame:
    """Dữ liệu khớp lệnh trong ngày. Hiện chỉ nguồn `vci` hỗ trợ."""
    return _to_df(_provider(source).intraday(symbol, page_size))


async def intraday_async(symbol: str, page_size: int = 100, source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).intraday_async(symbol, page_size))
