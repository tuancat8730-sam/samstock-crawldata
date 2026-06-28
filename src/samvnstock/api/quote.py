from collections.abc import Sequence

import pandas as pd
from pydantic import BaseModel

import samvnstock.providers.vci  # noqa: F401  (registers the "vci" provider)
import samvnstock.providers.vnd  # noqa: F401  (registers the "vnd" provider)
from samvnstock.core.registry import ProviderRegistry
from samvnstock.providers.base import QuoteProvider


def _provider(source: str) -> QuoteProvider:
    provider_cls = ProviderRegistry.get("quote", source)
    return provider_cls()  # type: ignore[no-any-return]


def _to_df(models: Sequence[BaseModel]) -> pd.DataFrame:
    return pd.DataFrame([m.model_dump() for m in models])


def history(symbol: str, start: str, end: str | None = None, source: str = "vci") -> pd.DataFrame:
    """Lịch sử giá OHLCV theo ngày cho một mã chứng khoán.

    `source="vci"` (mặc định) hoặc `source="vnd"` (nguồn dự phòng, nhanh hơn,
    dùng khi VCI bị chặn IP — ví dụ trên Google Colab/Kaggle).
    """
    return _to_df(_provider(source).history(symbol, start, end))


async def history_async(
    symbol: str, start: str, end: str | None = None, source: str = "vci"
) -> pd.DataFrame:
    return _to_df(await _provider(source).history_async(symbol, start, end))


def intraday(symbol: str, page_size: int = 100, source: str = "vci") -> pd.DataFrame:
    """Dữ liệu khớp lệnh trong ngày. Hiện chỉ nguồn `vci` hỗ trợ."""
    return _to_df(_provider(source).intraday(symbol, page_size))


async def intraday_async(symbol: str, page_size: int = 100, source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).intraday_async(symbol, page_size))
