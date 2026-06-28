# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/),
tuân theo [Semantic Versioning](https://semver.org/lang/vi/).

## [0.3.0] - Unreleased

### Added

- `core/cache.py`: `ParquetCache` — cache parquet trên đĩa theo khoá
  `(kind, source, symbol, params)`, có TTL (mặc định 24h, lưu tại
  `~/.cache/samvnstock`). Áp dụng cho `api/company.py` qua tham số
  `use_cache=True` (opt-in, chỉ ở bản sync).
- `core/models.py`: `CompanyOverview`, `Shareholder`, `Officer`, `Subsidiary`,
  `CompanyEvent`, `NewsItem`, `FinancialRow` (long-format — dùng chung cho
  Company.ratio_summary và Finance ở v0.4).
- `providers/base.py`: `CompanyProvider` ABC (chỉ `overview` là bắt buộc).
- VCI: `Company.overview`, `.shareholders`, `.officers`, `.subsidiaries`,
  `.events`, `.news`, `.ratio_summary` — endpoint xác minh từ mã nguồn mở
  `thinh-vu/vnstock` (`explorer/vci/company.py`).
- `api/company.py`: facade cho toàn bộ method trên (sync + async).

### Known limitations

- `events`/`news`: tên trường tiêu đề (`event_title`, `title`) là **best-effort**
  — chính `vnstock` cũng không chuẩn hoá cứng các trường này (chỉ generic
  camelCase→snake_case + drop một số cột), nên tên trường thật của VCI cho các
  endpoint này chưa được xác minh 100%. Nếu dữ liệu trả về sai/thiếu, cần mẫu
  response thật để sửa field map trong `providers/vci/company.py`.
- Không thể live-test trực tiếp các endpoint `iq.vietcap.com.vn` (bao gồm
  Company) từ môi trường phát triển hiện tại — bị trả 403 khi gọi không có
  header browser-like đầy đủ (qua WebFetch). Endpoint được tin dùng dựa trên
  việc tham chiếu mã nguồn mở vnstock, không phải gọi thử trực tiếp; test ở
  mức unit (respx mock), chưa có integration test thật.

## [0.2.0] - 2026-06-28

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
