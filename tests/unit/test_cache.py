import pandas as pd

from samvnstock.core.cache import ParquetCache


def test_set_then_get_round_trips_dataframe(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = ParquetCache(cache_dir=tmp_path, ttl_seconds=3600)
    df = pd.DataFrame([{"symbol": "VCB", "value": 1.5}])

    cache.set("company", "vci", "VCB", df, params={"method": "overview"})
    result = cache.get("company", "vci", "VCB", params={"method": "overview"})

    assert result is not None
    pd.testing.assert_frame_equal(result, df)


def test_get_returns_none_when_not_cached(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = ParquetCache(cache_dir=tmp_path)

    assert cache.get("company", "vci", "VCB") is None


def test_get_returns_none_when_expired(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = ParquetCache(cache_dir=tmp_path, ttl_seconds=0)
    df = pd.DataFrame([{"symbol": "VCB"}])

    cache.set("company", "vci", "VCB", df)
    import time

    time.sleep(0.05)

    assert cache.get("company", "vci", "VCB") is None


def test_different_params_use_different_cache_entries(tmp_path) -> None:  # type: ignore[no-untyped-def]
    cache = ParquetCache(cache_dir=tmp_path)
    df_overview = pd.DataFrame([{"method": "overview"}])
    df_officers = pd.DataFrame([{"method": "officers"}])

    cache.set("company", "vci", "VCB", df_overview, params={"method": "overview"})
    cache.set("company", "vci", "VCB", df_officers, params={"method": "officers"})

    cached_overview = cache.get("company", "vci", "VCB", params={"method": "overview"})
    cached_officers = cache.get("company", "vci", "VCB", params={"method": "officers"})
    assert cached_overview["method"][0] == "overview"
    assert cached_officers["method"][0] == "officers"
