from datetime import datetime
from typing import Any

from samvnstock.core.client import HttpClient
from samvnstock.core.exceptions import SourceError
from samvnstock.core.models import Bar
from samvnstock.core.validate import filter_valid_bars
from samvnstock.providers.base import QuoteProvider
from samvnstock.providers.vnd.const import HEADERS, INTERVAL_RESOLUTION_MAP, QUOTE_HISTORY_URL
from samvnstock.utils.datetime import end_of_day_timestamp, parse_date


class VndQuoteProvider(QuoteProvider):
    """Quote provider backed by VNDIRECT's public `dchart` TradingView UDF feed.

    Used as a fallback OHLCV source to VCI (which is sometimes IP-blocked on
    cloud providers). Unlike VCI, dchart-api natively supports "1m", "5m",
    "15m", "30m", "1H", and "1D" (default) without client-side resampling.
    """

    def __init__(self, client: HttpClient | None = None) -> None:
        self._client = client or HttpClient(headers=HEADERS)

    def history(
        self, symbol: str, start: str, end: str | None = None, interval: str = "1D"
    ) -> list[Bar]:
        params = self._build_params(symbol, start, end, interval)
        data = self._client.get(QUOTE_HISTORY_URL, params=params)
        return self._parse(data, symbol)

    async def history_async(
        self, symbol: str, start: str, end: str | None = None, interval: str = "1D"
    ) -> list[Bar]:
        params = self._build_params(symbol, start, end, interval)
        data = await self._client.aget(QUOTE_HISTORY_URL, params=params)
        return self._parse(data, symbol)

    def _build_params(
        self, symbol: str, start: str, end: str | None, interval: str
    ) -> dict[str, Any]:
        resolution = INTERVAL_RESOLUTION_MAP.get(interval)
        if resolution is None:
            raise ValueError(
                f"VND không hỗ trợ interval '{interval}'. "
                f"Dùng một trong {sorted(INTERVAL_RESOLUTION_MAP)}."
            )

        start_dt = parse_date(start)
        end_dt = parse_date(end) if end else datetime.now()
        return {
            "resolution": resolution,
            "symbol": symbol,
            "from": int(start_dt.timestamp()),
            "to": end_of_day_timestamp(end_dt),
        }

    def _parse(self, data: Any, symbol: str) -> list[Bar]:
        if not isinstance(data, dict) or data.get("s") != "ok":
            raise SourceError(f"Không tìm thấy dữ liệu lịch sử giá VND cho {symbol}")

        required_keys = ("t", "o", "h", "l", "c", "v")
        if not all(key in data for key in required_keys):
            raise SourceError(f"Dữ liệu trả về từ VND thiếu trường OHLCV cho {symbol}")

        bars = []
        columns = (data["t"], data["o"], data["h"], data["l"], data["c"], data["v"])
        for t, o, h, l, c, v in zip(*columns, strict=True):  # noqa: E741
            bars.append(
                Bar(
                    symbol=symbol,
                    time=datetime.fromtimestamp(t),
                    open=o,
                    high=h,
                    low=l,
                    close=c,
                    volume=int(v),
                )
            )
        return filter_valid_bars(bars)
