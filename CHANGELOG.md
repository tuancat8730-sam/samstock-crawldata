# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/),
tuân theo [Semantic Versioning](https://semver.org/lang/vi/).

## [0.5.0] - Unreleased

### Added

- `core/validate.py`: `is_valid_bar`/`filter_valid_bars` — loại bỏ dòng OHLCV
  vô lý (`high < low`, `high < open/close`, `low > open/close`, volume âm)
  trước khi trả cho người dùng. Áp dụng cho cả VCI và VND `Quote.history`.
- `utils/datetime.py`: `estimate_bar_count` — ước lượng `countBack` cho VCI
  theo timeFrame (ONE_DAY/ONE_HOUR/ONE_MINUTE), tương tự logic vnstock.
- `Quote.history` hỗ trợ tham số `interval`:
  - VCI: `"1D"` (mặc định), `"1H"`, `"1m"` — map trực tiếp `timeFrame` của VCI.
    **Không** hỗ trợ `"5m"/"15m"/"30m"` vì cần resample phía client (chưa làm).
  - VND: `"1D"`, `"1H"`, `"30m"`, `"15m"`, `"5m"`, `"1m"` — `dchart-api` hỗ trợ
    native cả 6 mức qua tham số `resolution`, không cần resample.
- `api/_fallback.py`: `with_fallback`/`with_fallback_async` — chỉ retry trên
  `SourceError`, không nuốt lỗi lập trình (`TypeError`...). Theo mục 6.4 của
  kế hoạch, chỉ áp dụng cho dữ liệu đã chuẩn hoá (Quote), không trộn báo cáo
  thô từ nhiều nguồn (Finance).
- `samvnstock.quote.history(..., source="auto")`: thử `vci` trước, tự chuyển
  sang `vnd` nếu lỗi (sync + async).

### Known limitations

- **Finance VND/MAS, Quote MAS chưa triển khai** (mục tiêu gốc của v0.5):
  domain thật của VND Finance (`finfo-api.vndirect.com.vn/v3/stocks/
  financialStatement`) đã xác nhận tồn tại qua nhiều nguồn độc lập nhưng
  **vẫn bị chặn DNS hoàn toàn** trong môi trường phát triển hiện tại (giống
  v0.2); tham số `modelTypes` của endpoint này là mã số nội bộ không có tài
  liệu công khai, ngay cả các thư viện khác cũng báo thiếu chỉ tiêu khi dùng
  — rủi ro sai cao nếu code mà không xác minh được field thật. MAS: vẫn không
  tìm được endpoint công khai nào.
- Phạm vi v0.5 đã thu hẹp lại theo thoả thuận với người dùng: thay Finance
  VND/MAS bằng fallback helper + validation OHLC + mở rộng interval Quote
  (vốn là việc bị hoãn từ v0.2).

## [0.4.0] - 2026-06-28

### Added

- `providers/base.py`: `FinanceProvider` ABC (`balance_sheet`, `income_statement`,
  `cashflow`, `ratio` bắt buộc; `note`, `annual_plan` mặc định
  `raise NotImplementedError`).
- `providers/_shared/finance_items.py`: `VCI_RATIO_ITEM_MAP` — ~25 chỉ tiêu
  ratio cốt lõi (P/E, P/B, ROE, ROA...), ánh xạ field thô VCI → `(item_code,
  item_name_vi)` chuẩn hoá, mở rộng dần theo gợi ý mục 3 của kế hoạch.
- VCI: `Finance.balance_sheet`, `.income_statement`, `.cashflow`, `.ratio` —
  endpoint xác minh từ `thinh-vu/vnstock` (`explorer/vci/financial.py`).
  **Phát hiện quan trọng:** VCI tự cung cấp cấu trúc cha-con (`parent` field)
  qua endpoint `financial-statement/metrics` — không chỉ MAS có cấu trúc này
  như giả định ban đầu trong kế hoạch; `parent_code` trong `FinancialRow` được
  điền từ chính VCI.
- `api/financial.py`: facade sync+async cho 4 method trên + `to_wide(df_long)`
  pivot long-format → wide (period × item_name). Cache opt-in giống
  `api/company.py` (key thêm `period`).

### Known limitations

- VCI `note` (thuyết minh BCTC) **chưa triển khai**: không có trong
  `explorer/vci/financial.py` của vnstock để tham chiếu kiến trúc, mặc dù kế
  hoạch gốc liệt kê là VCI có.
- Field map `ratio()` (`VCI_RATIO_ITEM_MAP`) chỉ phủ ~25 chỉ tiêu phổ biến —
  các trường còn lại trong response thực tế (nếu có) bị bỏ qua âm thầm; mở
  rộng dict khi cần thêm chỉ tiêu.
- Vẫn chưa thể live-test các endpoint `iq.vietcap.com.vn` từ môi trường phát
  triển hiện tại (như đã ghi ở v0.3) — độ tin cậy dựa trên việc đọc mã nguồn
  mở vnstock, chưa có integration test thật; chỉ có unit test mock (respx).

## [0.3.0] - 2026-06-28

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
