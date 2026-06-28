from datetime import datetime
from typing import Any

from samvnstock.core.client import HttpClient
from samvnstock.core.exceptions import SourceError
from samvnstock.core.models import Bar, Tick
from samvnstock.core.normalize import remap
from samvnstock.core.validate import filter_valid_bars
from samvnstock.providers.base import QuoteProvider
from samvnstock.providers.vci.const import (
    HEADERS,
    INTERVAL_TIME_FRAME_MAP,
    INTRADAY_FIELD_MAP,
    QUOTE_HISTORY_URL,
    QUOTE_INTRADAY_URL,
)
from samvnstock.utils.datetime import end_of_day_timestamp, estimate_bar_count, parse_date


class VciQuoteProvider(QuoteProvider):
    """Quote provider backed by VCI's `chart/OHLCChart/gap-chart` and
    `market-watch/LEData/getAll` endpoints.

    `history` supports "1D" (default), "1H", and "1m" — these map directly to
    VCI's native `timeFrame` values. "5m"/"15m"/"30m" would need client-side
    resampling of 1-minute bars (not implemented here); use `source="vnd"`
    for those, since VNDIRECT's feed supports them natively.
    """

    def __init__(self, client: HttpClient | None = None) -> None:
        self._client = client or HttpClient(headers=HEADERS)

    def history(
        self, symbol: str, start: str, end: str | None = None, interval: str = "1D"
    ) -> list[Bar]:
        payload = self._build_payload(symbol, start, end, interval)
        data = self._client.post(QUOTE_HISTORY_URL, json=payload)
        return self._parse(data, symbol)

    async def history_async(
        self, symbol: str, start: str, end: str | None = None, interval: str = "1D"
    ) -> list[Bar]:
        payload = self._build_payload(symbol, start, end, interval)
        data = await self._client.apost(QUOTE_HISTORY_URL, json=payload)
        return self._parse(data, symbol)

    def intraday(self, symbol: str, page_size: int = 100) -> list[Tick]:
        payload = {"symbol": symbol, "limit": page_size, "truncTime": None}
        data = self._client.post(QUOTE_INTRADAY_URL, json=payload)
        return self._parse_intraday(data, symbol)

    async def intraday_async(self, symbol: str, page_size: int = 100) -> list[Tick]:
        payload = {"symbol": symbol, "limit": page_size, "truncTime": None}
        data = await self._client.apost(QUOTE_INTRADAY_URL, json=payload)
        return self._parse_intraday(data, symbol)

    def _build_payload(
        self, symbol: str, start: str, end: str | None, interval: str
    ) -> dict[str, Any]:
        time_frame = INTERVAL_TIME_FRAME_MAP.get(interval)
        if time_frame is None:
            raise ValueError(
                f"VCI không hỗ trợ trực tiếp interval '{interval}'. "
                f"Dùng một trong {sorted(INTERVAL_TIME_FRAME_MAP)}, "
                f"hoặc source='vnd' cho 5m/15m/30m."
            )

        start_dt = parse_date(start)
        end_dt = parse_date(end) if end else datetime.now()
        count_back = estimate_bar_count(start_dt, end_dt, time_frame)
        return {
            "timeFrame": time_frame,
            "symbols": [symbol],
            "to": end_of_day_timestamp(end_dt),
            "countBack": count_back,
        }

    def _parse_intraday(self, data: Any, symbol: str) -> list[Tick]:
        if isinstance(data, dict) and "data" in data:
            data = data["data"]
        if not isinstance(data, list):
            raise SourceError(f"Không tìm thấy dữ liệu khớp lệnh cho {symbol}")

        ticks = []
        for raw in data:
            row = remap(raw, INTRADAY_FIELD_MAP)
            if "time" not in row or "price" not in row:
                continue
            ticks.append(
                Tick(
                    symbol=symbol,
                    time=datetime.fromtimestamp(row["time"]),
                    price=row["price"],
                    volume=int(row.get("volume", 0)),
                    match_type=row.get("match_type"),
                )
            )
        return ticks

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
        return filter_valid_bars(bars)
