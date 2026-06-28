# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/),
tuân theo [Semantic Versioning](https://semver.org/lang/vi/).

## [0.2.0] - Unreleased

### Added

- `core/normalize.py`: `remap`, `to_float`, `to_int`.
- `core/client.py`: rate-limit (fixed-interval) cho `HttpClient`, dùng tham số
  `requests_per_second`.
- `core/exceptions.py`: `SourceUnavailableError`.
- `core/models.py`: `Tick`, `Industry`, `SymbolIndustry`.
- `providers/base.py`: `ListingProvider` mở rộng (`industry`,
  `symbols_by_exchange`, `symbols_by_group`, `symbols_by_industries`);
  `QuoteProvider` mở rộng (`intraday`). Method mới mặc định
  `raise NotImplementedError` để nguồn không hỗ trợ không bị buộc cài đặt.
- VCI: `Listing.industry`, `.symbols_by_exchange`, `.symbols_by_group`,
  `.symbols_by_industries`; `Quote.intraday`.
- Nguồn mới **VND** (`providers/vnd/`): `Quote.history` qua API công khai
  `dchart-api.vndirect.com.vn` (TradingView UDF), dùng làm dự phòng cho VCI.
- `api/listing.py`, `api/quote.py`: facade cho toàn bộ method mới (sync + async).

### Known limitations

- VND `Listing.all_symbols` **chưa triển khai**: endpoint bulk listing công khai
  (`finfo-api.vndirect.com.vn`) không gọi được từ môi trường phát triển hiện tại
  để xác minh; endpoint search-as-you-type của `dchart-api` không đủ tin cậy cho
  bulk listing.
- VCI `price_depth`, `trading_stats`, `side_stats`: không có trong mã nguồn mở
  `thinh-vu/vnstock` để tham chiếu kiến trúc — chưa triển khai.
- Nguồn **MAS**, **CafeF**: chỉ được mô tả trong tài liệu sản phẩm trả phí
  "Vnstock_data" (`vnstock-hq/vnstock-agent-guide`), không có endpoint công khai
  đã xác minh — chưa triển khai.

## [0.1.0] - 2026-06-28

### Added

- Khung repo: `pyproject.toml` (hatchling), license MIT, ruff/mypy/pytest/pre-commit,
  GitHub Actions CI.
- `core/`: `client.py` (httpx sync+async, retry/backoff), `models.py` (`Bar`, `Symbol`),
  `registry.py`, `exceptions.py`.
- Nguồn **VCI**: `Listing.all_symbols`, `Quote.history` (OHLCV theo ngày).
- `api/listing.py`, `api/quote.py`: facade trả về `pandas.DataFrame`.
