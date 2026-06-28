# Kế hoạch xây dựng thư viện Python dữ liệu chứng khoán Việt Nam

> Phân tích `thinh-vu/vnstock` (~1.341★) và kế hoạch chi tiết để bạn xây thư viện mã nguồn mở của riêng mình.
> Mục tiêu: thư viện Python lấy dữ liệu CK Việt Nam, open-source.

---

## Phần 1 — Phân tích vnstock: học gì từ repo dẫn đầu

### 1.1. Tổng quan

vnstock không chỉ là "crawler giá cổ phiếu". Nó là một **nền tảng dữ liệu tài chính** có kiến trúc nhiều lớp, hỗ trợ: cổ phiếu, chỉ số (VNIndex/HNX/UPCOM), chứng quyền (CW), phái sinh (VN30F), trái phiếu, quỹ (ETF/quỹ mở), forex, crypto, vàng, tin tức & sự kiện. Đây là lý do nó vượt xa các repo khác về số sao.

Điểm mấu chốt giúp nó thành công và bạn nên sao chép về mặt *thiết kế*:

1. **Trừu tượng hoá nguồn dữ liệu (provider/adapter pattern).** Mỗi nguồn (VCI, KBS, MSN, FMarket...) là một "explorer" độc lập nhưng cùng tuân theo một giao diện chung. Người dùng chỉ cần đổi tham số `source=` mà không phải sửa code.
2. **Lớp API hợp nhất (unified facade).** Người dùng gọi `Quote`, `Company`, `Financial`, `Listing`, `Trading` — không cần biết bên dưới đang gọi nguồn nào.
3. **Chuẩn hoá trường dữ liệu (field normalization).** Mỗi nguồn trả tên cột khác nhau; có một lớp mapper/normalizer đưa tất cả về một schema thống nhất.
4. **Hạ tầng HTTP bền bỉ.** Có proxy manager, xoay user-agent, giả lập browser profile để chống chặn (anti-bot) — phần "khó nhằn" nhất khi crawl dữ liệu CK Việt Nam.
5. **Kỹ thuật phần mềm nghiêm túc.** Có test (unit/integration), CI/CD (GitHub Actions), pre-commit, type models, logging, exceptions riêng, CHANGELOG, docs.

### 1.2. Cấu trúc thư mục thực tế (rút gọn)

```
vnstock/
├── __init__.py            # export public API
├── base.py, config.py, constants.py
├── api/                   # LỚP FACADE công khai (source-agnostic)
│   ├── quote.py           #   giá lịch sử / intraday
│   ├── company.py         #   hồ sơ doanh nghiệp
│   ├── financial.py       #   báo cáo tài chính
│   ├── listing.py         #   danh sách mã / sàn
│   └── trading.py         #   bảng giá, khớp lệnh
├── common/                # client, data, indices, viz (tiện ích dùng chung)
├── core/                  # ĐỘNG CƠ
│   ├── base/              #   provider.py, registry.py (abstract base)
│   ├── config/            #   hằng số, cấu hình môi trường (vd Google Colab)
│   ├── converter/         #   export ra csv/excel...
│   ├── utils/             #   "kho vũ khí":
│   │   ├── client.py            HTTP client
│   │   ├── proxy_manager.py     quản lý proxy
│   │   ├── user_agent.py        xoay UA
│   │   ├── browser_profiles.py  giả lập browser
│   │   ├── field/               handler, mapper, normalizer, validator
│   │   ├── transform.py, parser.py, interval.py, lookback.py
│   │   ├── logger.py, env.py, auth.py, upgrade.py ...
│   ├── models.py, types.py, exceptions.py, settings.py, registry.py
├── explorer/              # ADAPTER THEO NGUỒN (phần quan trọng nhất)
│   ├── vci/               #   VCI: company, financial, listing, quote, trading
│   ├── kbs/               #   KB Securities (đủ bộ tương tự)
│   ├── msn/               #   MSN (dữ liệu quốc tế)
│   ├── fmarket/           #   quỹ mở/ETF
│   └── misc/              #   exchange_rate, gold_price
├── connector/             # kết nối broker (dnse trade, fmp)
├── ui/                    # lớp giao diện theo "domain" (market/bond, crypto, fundamental...)
└── bot/                   # notify (telegram)

tests/    -> unit/, integration/, fixtures/, examples/
.github/workflows/  -> test, code-quality, coverage, performance
pyproject.toml, requirements.txt, Makefile, .pre-commit-config.yaml, CHANGELOG.md
```

### 1.3. Các design pattern cốt lõi (đây là thứ đáng học nhất)

| Pattern | Vai trò | File tham chiếu trong vnstock |
|---|---|---|
| **Adapter / Provider** | Mỗi nguồn dữ liệu là một module cùng interface | `explorer/vci/*`, `explorer/kbs/*` |
| **Registry** | Đăng ký & tra cứu provider theo tên nguồn | `core/registry.py`, `core/base/registry.py` |
| **Facade** | API công khai gọn, giấu chi tiết nguồn | `api/*`, `ui/*` |
| **Strategy (field mapping)** | Mỗi nguồn có chiến lược map cột riêng | `core/utils/field/mapper.py`, `normalizer.py` |
| **DTO / Models** | Chuẩn hoá kiểu dữ liệu trả về | `core/models.py`, `core/types.py` |

### 1.4. Lưu ý về giấy phép (rất quan trọng cho bạn)

vnstock dùng **custom license, KHÔNG cho mục đích thương mại** và yêu cầu trích dẫn. Vì vậy:

- **Không** copy code của vnstock vào repo của bạn.
- Bạn được phép học **kiến trúc, ý tưởng, pattern** (không có bản quyền đối với ý tưởng) và tự viết lại từ đầu.
- Nếu muốn repo của bạn thực sự "mở" và thân thiện cộng đồng, chọn **MIT hoặc Apache-2.0** — khác biệt rõ với vnstock và là lợi thế cạnh tranh (nhiều người cần license thương mại sẽ tìm đến bạn).

---

## Phần 2 — Kế hoạch xây repo của bạn

### 2.1. Định vị & khác biệt hoá

Đừng clone 1:1. Vào sau, bạn cần một góc khác biệt. Một số hướng định vị khả thi:

- **"Permissive license"**: MIT/Apache, dùng được cho cả mục đích thương mại → thu hút dev và doanh nghiệp.
- **Async-first**: hỗ trợ `asyncio` + tải song song nhiều mã (vnstock chủ yếu đồng bộ) → nhanh hơn rõ rệt khi quét cả thị trường.
- **Type-safe & hiện đại**: Pydantic v2 cho toàn bộ model, typing đầy đủ, hỗ trợ Polars song song với pandas.
- **Tích hợp cache thông minh**: cache đĩa (parquet) để giảm gọi API lặp lại — điều người dùng rất cần.

> Gợi ý: chọn **1–2 điểm khác biệt** làm "bán hàng" chính, đừng ôm hết.

### 2.2. Tên & chuẩn bị

- Đặt tên package ngắn, dễ nhớ, chưa bị chiếm trên PyPI (kiểm tra tại pypi.org). Ví dụ dạng: `vnquant-x`, `vnmarket`, `pystock-vn`...
- Tạo tài khoản PyPI + TestPyPI, GitHub repo, bật Discussions & Issues templates.

### 2.3. Kiến trúc đề xuất cho repo của bạn

Bám sát triết lý vnstock nhưng tinh gọn hơn ở giai đoạn đầu:

```
yourpkg/
├── __init__.py              # export Quote, Listing, Company, Financial, Trading
├── core/
│   ├── client.py            # HTTP client (httpx), retry, timeout, rate-limit
│   ├── proxy.py             # (tuỳ chọn) xoay proxy / user-agent
│   ├── cache.py             # cache parquet theo (symbol, interval, range)
│   ├── models.py            # Pydantic models: Bar, CompanyProfile, FinancialReport...
│   ├── registry.py          # đăng ký provider theo tên nguồn
│   ├── exceptions.py        # lỗi riêng: SourceError, RateLimitError, SymbolNotFound
│   ├── normalize.py         # chuẩn hoá tên cột -> schema chung
│   └── logging.py
├── providers/               # = "explorer" của vnstock
│   ├── base.py              # lớp abstract: QuoteProvider, ListingProvider...
│   └── vci/                 # nguồn đầu tiên (chọn 1 nguồn ổn định để khởi đầu)
│       ├── quote.py
│       ├── listing.py
│       ├── company.py
│       └── financial.py
├── api/                     # facade công khai source-agnostic
│   ├── quote.py
│   ├── listing.py
│   ├── company.py
│   └── financial.py
└── utils/
    ├── interval.py          # parse '1D','1H','1m'...
    └── datetime.py          # xử lý phiên giao dịch, lịch nghỉ lễ
```

Nguyên tắc thiết kế:

1. **Thêm nguồn = thêm một thư mục trong `providers/`** — không đụng tới `api/`.
2. **`api/` chỉ gọi qua registry**, người dùng truyền `source="vci"`.
3. **Mọi dữ liệu trả về đi qua `normalize.py`** → cùng tên cột bất kể nguồn.
4. **Mọi I/O mạng nằm trong `core/client.py`** — dễ test (mock 1 chỗ).

### 2.4. Tech stack đề xuất

| Hạng mục | Lựa chọn | Ghi chú |
|---|---|---|
| HTTP | `httpx` | Hỗ trợ async + sync cùng API |
| Data | `pandas` (bắt buộc), `polars` (tuỳ chọn) | Trả về DataFrame |
| Validation | `pydantic` v2 | Models & settings |
| Cache | `pyarrow`/parquet | Giảm gọi API lặp |
| Test | `pytest`, `pytest-cov`, `responses`/`respx` | Mock HTTP |
| Lint/format | `ruff` (gộp flake8+isort+black) | Nhanh, 1 công cụ |
| Type check | `mypy` | CI gate |
| Build/đóng gói | `hatchling` + `pyproject.toml` | Chuẩn PEP 621 |
| Docs | `mkdocs-material` | Đẹp, dễ viết, song ngữ |
| CI/CD | GitHub Actions | test + publish PyPI |
| Pre-commit | `pre-commit` | ruff + mypy trước mỗi commit |

### 2.5. Phạm vi dữ liệu theo giai đoạn (MVP → mở rộng)

Đừng làm hết một lúc. Thứ tự đề xuất theo độ "đắt giá / dễ làm":

- **MVP (v0.1):** Listing (danh sách mã, theo sàn) + Quote lịch sử (OHLCV theo ngày). Đây là 80% nhu cầu.
- **v0.2:** Quote intraday + bảng giá (price board) realtime.
- **v0.3:** Company profile + cổ đông + ban lãnh đạo.
- **v0.4:** Financial reports (cân đối, KQKD, lưu chuyển tiền tệ, chỉ số).
- **v0.5:** Chỉ số thị trường (VNIndex/HNX/UPCOM), phái sinh (VN30F).
- **v0.6+:** Quỹ/ETF, trái phiếu, CW, forex/vàng/crypto, tin tức.

### 2.6. Roadmap thực thi (gợi ý theo tuần)

**Giai đoạn 0 — Khởi tạo (Tuần 1)**
- [ ] Khởi tạo repo, `pyproject.toml`, cấu trúc thư mục, license (MIT/Apache).
- [ ] Cấu hình ruff + mypy + pre-commit + pytest.
- [ ] GitHub Actions: chạy lint + test trên push/PR.
- [ ] README khung + CONTRIBUTING + issue templates.

**Giai đoạn 1 — Lõi + MVP (Tuần 2–3)**
- [ ] `core/client.py` (httpx, retry, rate-limit) + test mock.
- [ ] `core/models.py` (Bar, Symbol) + `normalize.py`.
- [ ] `providers/base.py` + provider VCI cho Listing & Quote.
- [ ] `api/listing.py`, `api/quote.py` qua registry.
- [ ] Test unit (mock HTTP) + 1 test integration (đánh dấu `@pytest.mark.network`).
- [ ] Publish `v0.1.0` lên TestPyPI rồi PyPI.

**Giai đoạn 2 — Mở rộng dữ liệu (Tuần 4–6)**
- [ ] Intraday + price board.
- [ ] Company + Financial.
- [ ] Thêm cache parquet.
- [ ] Docs site (mkdocs) + ví dụ notebook.

**Giai đoạn 3 — Đa nguồn & cộng đồng (Tuần 7+)**
- [ ] Thêm nguồn thứ 2 (vd TCBS/SSI) → kiểm chứng tính trừu tượng hoá.
- [ ] Fallback tự động khi 1 nguồn lỗi.
- [ ] Coverage > 80%, badge, CHANGELOG theo Keep a Changelog.
- [ ] Viết bài giới thiệu, đăng cộng đồng (group Facebook, Reddit, Viblo).

### 2.7. Chất lượng & vận hành (yếu tố quyết định số sao)

- **Test mạng tách biệt:** mock toàn bộ trong CI; test thật chạy thủ công/định kỳ (cron) để phát hiện nguồn đổi API — vnstock có hẳn workflow `verify-api-key` và `performance` cho việc này.
- **Versioning chặt (SemVer)** + CHANGELOG → người dùng tin tưởng nâng cấp.
- **Xử lý nguồn đổi cấu trúc:** API các CTCK VN hay đổi bất ngờ; tách "endpoint + field map" thành config để sửa nhanh không cần đổi logic.
- **Docs song ngữ Việt–Anh** như vnstock → tiếp cận cả cộng đồng quốc tế.
- **Disclaimer pháp lý** rõ ràng (dữ liệu chỉ cho nghiên cứu/cá nhân, không phải khuyến nghị đầu tư).

### 2.8. Rủi ro & cách giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| Nguồn (CTCK) đổi/đóng API | Đa nguồn + tách config endpoint; cảnh báo qua CI cron |
| Bị chặn IP/anti-bot | Rate-limit lịch sự, xoay UA/proxy, cache mạnh |
| Vấn đề bản quyền dữ liệu | Disclaimer; chỉ truy cập API công khai; không phân phối lại dữ liệu thô |
| Khó cạnh tranh vnstock | Khác biệt hoá (license mở, async, cache, type-safe) |
| Bỏ dở giữa chừng | Làm MVP nhỏ, release sớm, lặp nhanh |

---

## Tóm tắt hành động ngay

1. Chốt **tên package** + **license MIT/Apache** + **1–2 điểm khác biệt**.
2. Dựng khung repo (Giai đoạn 0) với CI + lint + test ngay từ commit đầu.
3. Làm **MVP = Listing + Quote lịch sử** với **1 nguồn (VCI)**, release `v0.1`.
4. Mở rộng dần theo roadmap; thêm nguồn thứ 2 để kiểm chứng kiến trúc.
```
```
*Lưu ý bản quyền: học kiến trúc & pattern là hợp pháp, nhưng không sao chép mã nguồn vnstock (license phi thương mại). Tự viết lại từ đầu.*
