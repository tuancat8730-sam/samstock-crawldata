from datetime import datetime
from typing import Any

from samvnstock.core.client import HttpClient
from samvnstock.core.exceptions import SourceError
from samvnstock.core.models import Bar
from samvnstock.providers.base import QuoteProvider
from samvnstock.providers.vci.const import HEADERS, QUOTE_HISTORY_URL, TIME_FRAME_DAY
from samvnstock.utils.datetime import count_business_days, end_of_day_timestamp, parse_date


class VciQuoteProvider(QuoteProvider):
    """Quote provider backed by VCI's `chart/OHLCChart/gap-chart` endpoint.

    v0.1 only supports daily ("1D") bars; intraday support is planned for v0.2.
    """

    def __init__(self, client: HttpClient | None = None) -> None:
        self._client = client or HttpClient(headers=HEADERS)

    def history(self, symbol: str, start: str, end: str | None = None) -> list[Bar]:
        payload = self._build_payload(symbol, start, end)
        data = self._client.post(QUOTE_HISTORY_URL, json=payload)
        return self._parse(data, symbol)

    async def history_async(
        self, symbol: str, start: str, end: str | None = None
    ) -> list[Bar]:
        payload = self._build_payload(symbol, start, end)
        data = await self._client.apost(QUOTE_HISTORY_URL, json=payload)
        return self._parse(data, symbol)

    def _build_payload(self, symbol: str, start: str, end: str | None) -> dict[str, Any]:
        start_dt = parse_date(start)
        end_dt = parse_date(end) if end else datetime.now()
        count_back = count_business_days(start_dt, end_dt) + 1
        return {
            "timeFrame": TIME_FRAME_DAY,
            "symbols": [symbol],
            "to": end_of_day_timestamp(end_dt),
            "countBack": count_back,
        }

    def _parse(self, data: Any, symbol: str) -> list[Bar]:
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        if not isinstance(data, list) or not data:
            raise SourceError(f"Không tìm thấy dữ liệu lịch sử giá cho {symbol}")

        series = data[0]
        required_keys = ("t", "o", "h", "l", "c", "v")
        if not all(key in series for key in required_keys):
            raise SourceError(f"Dữ liệu trả về từ VCI thiếu trường OHLCV cho {symbol}")

        bars = []
        columns = (series["t"], series["o"], series["h"], series["l"], series["c"], series["v"])
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
