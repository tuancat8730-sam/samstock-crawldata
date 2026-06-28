# VNDIRECT's dchart-api is a public TradingView UDF-compatible feed used by
# their own web charts (dchart.vndirect.com.vn). Verified manually:
# GET /dchart/history?resolution=D&symbol=VCB&from=<unix>&to=<unix>
# -> {"t": [...], "o": [...], "h": [...], "l": [...], "c": [...], "v": [...], "s": "ok"}
BASE_URL = "https://dchart-api.vndirect.com.vn/dchart/"
QUOTE_HISTORY_URL = BASE_URL + "history"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://dchart.vndirect.com.vn/",
    "Origin": "https://dchart.vndirect.com.vn/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
}

RESOLUTION_DAY = "D"

# `resolution` values natively supported by dchart-api (confirmed via the
# `/dchart/symbols` metadata endpoint: supported_resolutions includes
# "1","5","15","30","60","D","W","M"). Unlike VCI, VND supports all of these
# server-side directly — no client resampling needed.
INTERVAL_RESOLUTION_MAP = {
    "1m": "1",
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1H": "60",
    "1D": "D",
}
