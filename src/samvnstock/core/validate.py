from samvnstock.core.models import Bar


def is_valid_bar(bar: Bar) -> bool:
    """Check basic OHLC sanity invariants that any well-formed bar must satisfy.

    Catches obviously corrupt rows (e.g. a broker API glitch) before they
    reach users, per [[KE-HOACH-CRAWL-DATA-CHI-TIET-1]] section 6.5.
    """
    if bar.high < bar.low:
        return False
    if bar.high < bar.open or bar.high < bar.close:
        return False
    if bar.low > bar.open or bar.low > bar.close:
        return False
    return bar.volume >= 0


def filter_valid_bars(bars: list[Bar]) -> list[Bar]:
    return [bar for bar in bars if is_valid_bar(bar)]
