import hashlib
import json
import time
from pathlib import Path
from typing import Any

import pandas as pd

_DEFAULT_CACHE_DIR = Path.home() / ".cache" / "samvnstock"


class ParquetCache:
    """On-disk parquet cache keyed by (kind, source, symbol, params), with TTL.

    Intended for data that changes rarely (Company) or sources that are
    flaky (per [[KE-HOACH-CRAWL-DATA-CHI-TIET-1]]) — callers opt in
    explicitly via `use_cache=True` on the relevant `api/` facade function.
    """

    def __init__(
        self, cache_dir: Path | str | None = None, ttl_seconds: float = 86400
    ) -> None:
        self._cache_dir = Path(cache_dir) if cache_dir else _DEFAULT_CACHE_DIR
        self._ttl_seconds = ttl_seconds

    def get(
        self, kind: str, source: str, symbol: str, params: dict[str, Any] | None = None
    ) -> pd.DataFrame | None:
        path = self._path_for(kind, source, symbol, params)
        if not path.exists():
            return None
        if time.time() - path.stat().st_mtime > self._ttl_seconds:
            return None
        return pd.read_parquet(path)

    def set(
        self,
        kind: str,
        source: str,
        symbol: str,
        df: pd.DataFrame,
        params: dict[str, Any] | None = None,
    ) -> None:
        path = self._path_for(kind, source, symbol, params)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path)

    def _path_for(
        self, kind: str, source: str, symbol: str, params: dict[str, Any] | None
    ) -> Path:
        key_payload = json.dumps(
            {"kind": kind, "source": source, "symbol": symbol, "params": params or {}},
            sort_keys=True,
        )
        key_hash = hashlib.sha256(key_payload.encode()).hexdigest()[:16]
        return self._cache_dir / kind / source / f"{symbol}_{key_hash}.parquet"
