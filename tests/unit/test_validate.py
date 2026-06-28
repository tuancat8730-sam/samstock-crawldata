from datetime import datetime

from samvnstock.core.models import Bar
from samvnstock.core.validate import filter_valid_bars, is_valid_bar


def _bar(**overrides: object) -> Bar:
    defaults = {
        "symbol": "VCB",
        "time": datetime(2024, 1, 1),
        "open": 10.0,
        "high": 11.0,
        "low": 9.0,
        "close": 10.5,
        "volume": 1000,
    }
    defaults.update(overrides)
    return Bar(**defaults)  # type: ignore[arg-type]


def test_valid_bar_passes() -> None:
    assert is_valid_bar(_bar()) is True


def test_high_below_low_is_invalid() -> None:
    assert is_valid_bar(_bar(high=8.0, low=9.0)) is False


def test_high_below_open_is_invalid() -> None:
    assert is_valid_bar(_bar(high=9.0, open=10.0, low=8.0)) is False


def test_low_above_close_is_invalid() -> None:
    assert is_valid_bar(_bar(low=11.0, close=10.5, high=12.0)) is False


def test_negative_volume_is_invalid() -> None:
    assert is_valid_bar(_bar(volume=-1)) is False


def test_filter_valid_bars_drops_only_invalid_rows() -> None:
    bars = [_bar(), _bar(high=1.0, low=9.0), _bar(close=10.8)]

    result = filter_valid_bars(bars)

    assert len(result) == 2
