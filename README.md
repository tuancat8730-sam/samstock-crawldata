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

# Lịch sử giá OHLCV theo ngày
df_quote = samvnstock.quote.history("VCB", start="2024-01-01", end="2024-06-30")

# Bản async tương đương
df_symbols = await samvnstock.listing.all_symbols_async()
df_quote = await samvnstock.quote.history_async("VCB", start="2024-01-01")
```

Nguồn dữ liệu hiện hỗ trợ: `vci` (mặc định). Thêm nguồn mới bằng cách đăng ký
provider qua `ProviderRegistry` — xem [CONTRIBUTING.md](./CONTRIBUTING.md).

## Roadmap

Xem chi tiết tại [KE-HOACH-XAY-REPO-CHUNG-KHOAN-VN.md](./KE-HOACH-XAY-REPO-CHUNG-KHOAN-VN.md).

- [x] v0.1 — Listing (`all_symbols`) + Quote lịch sử theo ngày (nguồn VCI, sync + async)
- [ ] v0.2 — Quote intraday + price board
- [ ] v0.3 — Company profile
- [ ] v0.4 — Financial reports
- [ ] v0.5+ — Chỉ số, phái sinh, quỹ/ETF, trái phiếu...

## Giấy phép & Disclaimer

MIT License — xem [LICENSE](./LICENSE).

Dữ liệu cung cấp qua thư viện này chỉ phục vụ mục đích nghiên cứu/cá nhân,
**không phải là khuyến nghị đầu tư**. Người dùng tự chịu trách nhiệm khi sử
dụng dữ liệu để ra quyết định đầu tư.
