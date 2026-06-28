BASE_URL = "https://trading.vietcap.com.vn/api/"
IQ_INSIGHT_URL = "https://iq.vietcap.com.vn/api/iq-insight-service"

LISTING_ALL_URL = BASE_URL + "price/symbols/getAll"
LISTING_BY_GROUP_URL = BASE_URL + "price/symbols/getByGroup"
ICB_CODES_URL = IQ_INSIGHT_URL + "/v1/sectors/icb-codes"
SYMBOLS_BY_INDUSTRIES_URL = IQ_INSIGHT_URL + "/v2/company/search-bar"

QUOTE_HISTORY_URL = BASE_URL + "chart/OHLCChart/gap-chart"
QUOTE_INTRADAY_URL = BASE_URL + "market-watch/LEData/getAll"

VCI_COMPANY_URL = IQ_INSIGHT_URL + "/v1/company"
COMPANY_EVENTS_URL = IQ_INSIGHT_URL + "/v1/events"
COMPANY_NEWS_URL = IQ_INSIGHT_URL + "/v1/news"

# `section` query param accepted by `/v1/company/{symbol}/financial-statement`.
FINANCE_SECTION_MAP = {
    "balance_sheet": "BALANCE_SHEET",
    "income_statement": "INCOME_STATEMENT",
    "cashflow": "CASH_FLOW",
}

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

# `timeFrame` values natively supported by VCI's gap-chart endpoint without
# client-side resampling. 5m/15m/30m would require resampling ONE_MINUTE bars
# client-side (not implemented) — use source="vnd" for those, which VNDIRECT's
# dchart-api supports natively.
INTERVAL_TIME_FRAME_MAP = {
    "1m": "ONE_MINUTE",
    "1H": "ONE_HOUR",
    "1D": "ONE_DAY",
}
TIME_FRAME_DAY = "ONE_DAY"

OHLC_FIELD_MAP = {"t": "time", "o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}

INTRADAY_FIELD_MAP = {
    "truncTime": "time",
    "matchPrice": "price",
    "matchVol": "volume",
    "matchType": "match_type",
}

# Index/derivative group codes accepted by `price/symbols/getByGroup`.
GROUP_CODES = {
    "HOSE": "HOSE",
    "HNX": "HNX",
    "UPCOM": "UPCOM",
    "VN30": "VN30",
    "VN100": "VN100",
    "HNX30": "HNX30",
    "ETF": "ETF",
    "CW": "CW",
    "BOND": "BOND",
}
