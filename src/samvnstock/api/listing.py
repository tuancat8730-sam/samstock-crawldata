from collections.abc import Sequence

import pandas as pd
from pydantic import BaseModel

import samvnstock.providers.vci  # noqa: F401  (registers the "vci" provider)
from samvnstock.core.registry import ProviderRegistry
from samvnstock.providers.base import ListingProvider


def _provider(source: str) -> ListingProvider:
    provider_cls = ProviderRegistry.get("listing", source)
    return provider_cls()  # type: ignore[no-any-return]


def _to_df(models: Sequence[BaseModel]) -> pd.DataFrame:
    return pd.DataFrame([m.model_dump() for m in models])


def all_symbols(source: str = "vci") -> pd.DataFrame:
    """Danh sách toàn bộ mã cổ phiếu (symbol, exchange, organ_name, type)."""
    return _to_df(_provider(source).all_symbols())


async def all_symbols_async(source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).all_symbols_async())


def symbols_by_exchange(source: str = "vci") -> pd.DataFrame:
    """Danh sách toàn bộ mã (mọi loại tài sản, không chỉ cổ phiếu), kèm sàn niêm yết."""
    return _to_df(_provider(source).symbols_by_exchange())


async def symbols_by_exchange_async(source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).symbols_by_exchange_async())


def symbols_by_group(group: str, source: str = "vci") -> list[str]:
    """Danh sách mã theo nhóm chỉ số/sàn (VN30, HNX30, HOSE, ETF...)."""
    return _provider(source).symbols_by_group(group)


async def symbols_by_group_async(group: str, source: str = "vci") -> list[str]:
    return await _provider(source).symbols_by_group_async(group)


def industry(source: str = "vci") -> pd.DataFrame:
    """Danh sách mã phân ngành ICB (icb_code, icb_name, level)."""
    return _to_df(_provider(source).industry())


async def industry_async(source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).industry_async())


def symbols_by_industries(source: str = "vci") -> pd.DataFrame:
    """Phân ngành ICB theo từng mã cổ phiếu (1 dòng / cấp ICB)."""
    return _to_df(_provider(source).symbols_by_industries())


async def symbols_by_industries_async(source: str = "vci") -> pd.DataFrame:
    return _to_df(await _provider(source).symbols_by_industries_async())
