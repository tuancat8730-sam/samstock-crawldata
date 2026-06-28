BASE_URL = "https://trading.vietcap.com.vn/api/"
LISTING_ALL_URL = BASE_URL + "price/symbols/getAll"
QUOTE_HISTORY_URL = BASE_URL + "chart/OHLCChart/gap-chart"

# Required so VCI's edge doesn't reject the request as non-browser traffic.
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Referer": "https://trading.vietcap.com.vn/",
    "Origin": "https://trading.vietcap.com.vn/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
}

# v0.1 only supports daily bars; intraday intervals are planned for v0.2.
TIME_FRAME_DAY = "ONE_DAY"

OHLC_FIELD_MAP = {"t": "time", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}
