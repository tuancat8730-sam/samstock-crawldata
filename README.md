# samvnstock

> Thư viện Python mã nguồn mở (MIT) để lấy dữ liệu chứng khoán Việt Nam.

[![CI](https://github.com/tuancat8730-sam/samstock-crawldata/actions/workflows/ci.yml/badge.svg)](https://github.com/tuancat8730-sam/samstock-crawldata/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Mục tiêu

`samvnstock` cung cấp một API thống nhất để truy cập dữ liệu thị trường chứng
khoán Việt Nam (giá lịch sử, danh sách mã, hồ sơ doanh nghiệp, báo cáo tài
chính...) từ nhiều nguồn khác nhau, với license MIT cho phép dùng cả trong môi
trường thương mại.

> ⚠️ Đang trong giai đoạn phát triển ban đầu (pre-MVP). API có thể thay đổi.

## Cài đặt

```bash
pip install samvnstock  # sẽ phát hành sau khi có v0.1.0
```

## Phát triển local

```bash
git clone git@github.com:tuancat8730-sam/samstock-crawldata.git
cd samstock-crawldata
pip install -e ".[dev]"
pre-commit install

ruff check .
mypy src
pytest
```

## Sử dụng

```python
import samvnstock

# Danh sách mã cổ phiếu (DataFrame)
df_symbols = samvnstock.listing.all_symbols()
df_all = samvnstock.listing.symbols_by_exchange()       # mọi loại tài sản, theo sàn
df_groups = samvnstock.listing.symbols_by_group("VN30")  # list[str]
df_icb = samvnstock.listing.industry()                   # mã phân ngành ICB
df_icb_map = samvnstock.listing.symbols_by_industries()   # phân ngành theo từng mã

# Lịch sử giá OHLCV theo ngày (mặc định nguồn VCI, fallback "vnd" khi VCI bị chặn IP)
df_quote = samvnstock.quote.history("VCB", start="2024-01-01", end="2024-06-30")
df_quote_vnd = samvnstock.quote.history("VCB", start="2024-01-01", source="vnd")

# Khớp lệnh trong ngày (chỉ nguồn vci)
df_intraday = samvnstock.quote.intraday("VCB")

# Bản async tương đương cho mọi hàm trên, hậu tố "_async"
df_symbols = await samvnstock.listing.all_symbols_async()
df_quote = await samvnstock.quote.history_async("VCB", start="2024-01-01")

# Hồ sơ doanh nghiệp (chỉ nguồn vci)
df_overview = samvnstock.company.overview("VCB")
df_shareholders = samvnstock.company.shareholders("VCB")
df_officers = samvnstock.company.officers("VCB")
df_subsidiaries = samvnstock.company.subsidiaries("VCB")
df_events = samvnstock.company.events("VCB")
df_news = samvnstock.company.news("VCB")
df_ratio = samvnstock.company.ratio_summary("VCB")  # long-format: item_name, value

# overview/shareholders/officers/subsidiaries/ratio_summary hỗ trợ cache đĩa
# (ít đổi -> cache 24h), opt-in qua use_cache=True
df_overview_cached = samvnstock.company.overview("VCB", use_cache=True)
```

Nguồn dữ liệu hiện hỗ trợ: `vci` (mặc định, đầy đủ nhất), `vnd` (chỉ
`Quote.history`, dùng làm dự phòng khi VCI bị chặn IP — ví dụ Google
Colab/Kaggle). Thêm nguồn mới bằng cách đăng ký provider qua
`ProviderRegistry` — xem [CONTRIBUTING.md](./CONTRIBUTING.md).

## Roadmap

Xem chi tiết tại [KE-HOACH-XAY-REPO-CHUNG-KHOAN-VN.md](./KE-HOACH-XAY-REPO-CHUNG-KHOAN-VN.md)
và [KE-HOACH-CRAWL-DATA-CHI-TIET-1.md](./KE-HOACH-CRAWL-DATA-CHI-TIET-1.md).

- [x] v0.1 — Listing (`all_symbols`) + Quote lịch sử theo ngày (nguồn VCI, sync + async)
- [x] v0.2 — Listing mở rộng (`industry`, `symbols_by_exchange`, `symbols_by_group`,
      `symbols_by_industries`, nguồn VCI) + Quote `intraday` (VCI) + Quote `history`
      nguồn `vnd` (dự phòng) + rate-limit cho `HttpClient`. **Không** gồm VND `all_symbols`,
      VCI `price_depth`/`trading_stats`/`side_stats`, và các nguồn MAS/CafeF — các
      endpoint này chỉ có trong tài liệu sản phẩm trả phí "Vnstock_data", không có
      trong mã nguồn mở hay API công khai nào tôi xác minh được; cần thêm thông tin
      trước khi triển khai để tránh code suy đoán không hoạt động thật.
- [x] v0.3 — Company profile (VCI: `overview`, `shareholders`, `officers`,
      `subsidiaries`, `events`, `news`, `ratio_summary`) + `core/cache.py`
      (parquet, TTL, opt-in qua `use_cache=True`). `events`/`news` dùng field map
      best-effort — xem CHANGELOG "Known limitations".
- [ ] v0.4 — Finance (VCI: balance_sheet/income_statement/cashflow/ratio, long-format)
- [ ] v0.5+ — Đa nguồn cho Finance/Quote, Trading, Market (tuỳ endpoint xác minh được)

## Giấy phép & Disclaimer

MIT License — xem [LICENSE](./LICENSE).

Dữ liệu cung cấp qua thư viện này chỉ phục vụ mục đích nghiên cứu/cá nhân,
**không phải là khuyến nghị đầu tư**. Người dùng tự chịu trách nhiệm khi sử
dụng dữ liệu để ra quyết định đầu tư.
