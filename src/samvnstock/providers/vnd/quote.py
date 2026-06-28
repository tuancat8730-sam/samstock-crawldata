from datetime import datetime
from typing import Any

from samvnstock.core.client import HttpClient
from samvnstock.core.exceptions import SourceError
from samvnstock.core.models import Bar
from samvnstock.providers.base import QuoteProvider
from samvnstock.providers.vnd.const import HEADERS, QUOTE_HISTORY_URL, RESOLUTION_DAY
from samvnstock.utils.datetime import end_of_day_timestamp, parse_date


class VndQuoteProvider(QuoteProvider):
    """Quote provider backed by VNDIRECT's public `dchart` TradingView UDF feed.

    Used as a fallback OHLCV source to VCI (which is sometimes IP-blocked on
    cloud providers); `history` only supports daily ("1D") bars for now.
    """

    def __init__(self, client: HttpClient | None = None) -> None:
        self._client = client or HttpClient(headers=HEADERS)

    def history(self, symbol: str, start: str, end: str | None = None) -> list[Bar]:
        params = self._build_params(symbol, start, end)
        data = self._client.get(QUOTE_HISTORY_URL, params=params)
        return self._parse(data, symbol)

    async def history_async(
        self, symbol: str, start: str, end: str | None = None
    ) -> list[Bar]:
        params = self._build_params(symbol, start, end)
        data = await self._client.aget(QUOTE_HISTORY_URL, params=params)
        return self._parse(data, symbol)

    def _build_params(self, symbol: str, start: str, end: str | None) -> dict[str, Any]:
        start_dt = parse_date(start)
        end_dt = parse_date(end) if end else datetime.now()
        return {
            "resolution": RESOLUTION_DAY,
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
        return bars
