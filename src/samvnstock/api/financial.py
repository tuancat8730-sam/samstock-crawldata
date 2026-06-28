from collections.abc import Callable, Sequence

import pandas as pd
from pydantic import BaseModel

import samvnstock.providers.vci  # noqa: F401  (registers the "vci" provider)
from samvnstock.core.cache import ParquetCache
from samvnstock.core.registry import ProviderRegistry
from samvnstock.providers.base import FinanceProvider

_cache = ParquetCache()


def _provider(source: str) -> FinanceProvider:
    provider_cls = ProviderRegistry.get("financial", source)
    return provider_cls()  # type: ignore[no-any-return]


def _to_df(models: Sequence[BaseModel]) -> pd.DataFrame:
    return pd.DataFrame([m.model_dump() for m in models])


def _cached(
    method: str,
    symbol: str,
    source: str,
    period: str,
    use_cache: bool,
    fetch: Callable[[], pd.DataFrame],
) -> pd.DataFrame:
    params = {"method": method, "period": period}
    if use_cache:
        cached_df = _cache.get("financial", source, symbol, params=params)
        if cached_df is not None:
            return cached_df

    df = fetch()

    if use_cache:
        _cache.set("financial", source, symbol, df, params=params)

    return df


def balance_sheet(
    symbol: str, period: str = "quarter", source: str = "vci", use_cache: bool = False
) -> pd.DataFrame:
    """Bảng cân đối kế toán, dạng long-format (symbol, period, item_code, item_name, value)."""
    return _cached(
        "balance_sheet",
        symbol,
        source,
        period,
        use_cache,
        lambda: _to_df(_provider(source).balance_sheet(symbol, period)),
    )


async def balance_sheet_async(
    symbol: str, period: str = "quarter", source: str = "vci"
) -> pd.DataFrame:
    return _to_df(await _provider(source).balance_sheet_async(symbol, period))


def income_statement(
    symbol: str, period: str = "quarter", source: str = "vci", use_cache: bool = False
) -> pd.DataFrame:
    """Báo cáo kết quả kinh doanh, dạng long-format."""
    return _cached(
        "income_statement",
        symbol,
        source,
        period,
        use_cache,
        lambda: _to_df(_provider(source).income_statement(symbol, period)),
    )


async def income_statement_async(
    symbol: str, period: str = "quarter", source: str = "vci"
) -> pd.DataFrame:
    return _to_df(await _provider(source).income_statement_async(symbol, period))


def cashflow(
    symbol: str, period: str = "quarter", source: str = "vci", use_cache: bool = False
) -> pd.DataFrame:
    """Báo cáo lưu chuyển tiền tệ, dạng long-format."""
    return _cached(
        "cashflow",
        symbol,
        source,
        period,
        use_cache,
        lambda: _to_df(_provider(source).cashflow(symbol, period)),
    )


async def cashflow_async(symbol: str, period: str = "quarter", source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).cashflow_async(symbol, period))


def ratio(
    symbol: str, period: str = "quarter", source: str = "vci", use_cache: bool = False
) -> pd.DataFrame:
    """Chỉ số tài chính (P/E, P/B, ROE, ROA...), dạng long-format."""
    return _cached(
        "ratio",
        symbol,
        source,
        period,
        use_cache,
        lambda: _to_df(_provider(source).ratio(symbol, period)),
    )


async def ratio_async(symbol: str, period: str = "quarter", source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).ratio_async(symbol, period))


def to_wide(df_long: pd.DataFrame) -> pd.DataFrame:
    """Pivot a long-format financial DataFrame to wide (period x item_name)."""
    return df_long.pivot_table(index="period", columns="item_name", values="value", aggfunc="first")
