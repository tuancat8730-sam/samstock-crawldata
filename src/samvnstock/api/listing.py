import pandas as pd

import samvnstock.providers.vci  # noqa: F401  (registers the "vci" provider)
from samvnstock.core.registry import ProviderRegistry
from samvnstock.providers.base import ListingProvider


def _provider(source: str) -> ListingProvider:
    provider_cls = ProviderRegistry.get("listing", source)
    return provider_cls()  # type: ignore[no-any-return]


def all_symbols(source: str = "vci") -> pd.DataFrame:
    """Danh sách toàn bộ mã cổ phiếu (symbol, exchange, organ_name, type)."""
    symbols = _provider(source).all_symbols()
    return pd.DataFrame([s.model_dump() for s in symbols])


async def all_symbols_async(source: str = "vci") -> pd.DataFrame:
    symbols = await _provider(source).all_symbols_async()
    return pd.DataFrame([s.model_dump() for s in symbols])
