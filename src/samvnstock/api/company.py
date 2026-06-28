from collections.abc import Callable, Sequence

import pandas as pd
from pydantic import BaseModel

import samvnstock.providers.vci  # noqa: F401  (registers the "vci" provider)
from samvnstock.core.cache import ParquetCache
from samvnstock.core.registry import ProviderRegistry
from samvnstock.providers.base import CompanyProvider

_cache = ParquetCache()


def _provider(source: str) -> CompanyProvider:
    provider_cls = ProviderRegistry.get("company", source)
    return provider_cls()  # type: ignore[no-any-return]


def _to_df(models: Sequence[BaseModel]) -> pd.DataFrame:
    return pd.DataFrame([m.model_dump() for m in models])


def _cached(
    method: str, symbol: str, source: str, use_cache: bool, fetch: Callable[[], pd.DataFrame]
) -> pd.DataFrame:
    if use_cache:
        cached_df = _cache.get("company", source, symbol, params={"method": method})
        if cached_df is not None:
            return cached_df

    df = fetch()

    if use_cache:
        _cache.set("company", source, symbol, df, params={"method": method})

    return df


def overview(symbol: str, source: str = "vci", use_cache: bool = False) -> pd.DataFrame:
    """Thông tin tổng quan công ty (organ_name, sector, company_profile, listing_date...).

    `use_cache=True` lưu kết quả vào parquet cache (mặc định ~/.cache/samvnstock,
    TTL 24h) — hữu ích vì thông tin công ty ít thay đổi.
    """
    return _cached(
        "overview", symbol, source, use_cache, lambda: _to_df([_provider(source).overview(symbol)])
    )


async def overview_async(symbol: str, source: str = "vci") -> pd.DataFrame:
    return _to_df([await _provider(source).overview_async(symbol)])


def shareholders(symbol: str, source: str = "vci", use_cache: bool = False) -> pd.DataFrame:
    """Danh sách cổ đông (share_holder, quantity, share_own_percent, update_date)."""
    return _cached(
        "shareholders",
        symbol,
        source,
        use_cache,
        lambda: _to_df(_provider(source).shareholders(symbol)),
    )


async def shareholders_async(symbol: str, source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).shareholders_async(symbol))


def officers(symbol: str, source: str = "vci", use_cache: bool = False) -> pd.DataFrame:
    """Ban lãnh đạo công ty (officer_name, officer_position, officer_own_percent...)."""
    return _cached(
        "officers", symbol, source, use_cache, lambda: _to_df(_provider(source).officers(symbol))
    )


async def officers_async(symbol: str, source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).officers_async(symbol))


def subsidiaries(symbol: str, source: str = "vci", use_cache: bool = False) -> pd.DataFrame:
    """Công ty con/liên kết (organ_name, ownership_percent, type)."""
    return _cached(
        "subsidiaries",
        symbol,
        source,
        use_cache,
        lambda: _to_df(_provider(source).subsidiaries(symbol)),
    )


async def subsidiaries_async(symbol: str, source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).subsidiaries_async(symbol))


def events(symbol: str, source: str = "vci") -> pd.DataFrame:
    """Sự kiện doanh nghiệp (cổ tức, ĐHCĐ, giao dịch nội bộ...)."""
    return _to_df(_provider(source).events(symbol))


async def events_async(symbol: str, source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).events_async(symbol))


def news(symbol: str, source: str = "vci") -> pd.DataFrame:
    """Tin tức liên quan đến công ty."""
    return _to_df(_provider(source).news(symbol))


async def news_async(symbol: str, source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).news_async(symbol))


def ratio_summary(symbol: str, source: str = "vci", use_cache: bool = False) -> pd.DataFrame:
    """Tóm tắt chỉ số tài chính, dạng long-format (item_name, value)."""
    return _cached(
        "ratio_summary",
        symbol,
        source,
        use_cache,
        lambda: _to_df(_provider(source).ratio_summary(symbol)),
    )


async def ratio_summary_async(symbol: str, source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).ratio_summary_async(symbol))
