# Kế hoạch chi tiết crawl dữ liệu — samvnstock (v0.2 → v0.7)

> Mở rộng từ v0.1 (Listing + Quote/VCI) để phủ đúng phạm vi bạn chọn trong
> [09-data-sources.md](https://github.com/vnstock-hq/vnstock-agent-guide/blob/main/docs/vnstock-data/09-data-sources.md),
> **giữ nguyên kiến trúc hiện có** (ABC provider sync+async → `ProviderRegistry` → facade `api/` trả `DataFrame`).

---

## 0. Hiện trạng (v0.1) — điểm xuất phát

Đã có và sẽ tái sử dụng nguyên vẹn:

- `core/registry.py` — `ProviderRegistry` keyed `(kind, source)`. **Không cần sửa**, đã đủ tổng quát cho mọi Lớp mới.
- `core/client.py` — `HttpClient` (`post`/`get` + `apost`/`aget`), inject được để mock.
- `core/models.py` — `Bar`, `Symbol` (Pydantic). Sẽ **bổ sung** model cho từng Lớp mới.
- `core/exceptions.py` — `SourceError`.
- `providers/base.py` — ABC `ListingProvider`, `QuoteProvider` (mỗi method có bản sync + `_async`).
- `providers/vci/` — `const.py` (HEADERS, URL), `__init__.py` (tự `register`), `quote.py`, `listing.py`.
- `api/` — facade convert `list[Model]` → `DataFrame`, có tham số `source=`, import package provider để kích hoạt đăng ký.

**Quy tắc vàng giữ nguyên:** thêm nguồn/Lớp = thêm file trong `providers/` + (nếu là Lớp mới) thêm ABC trong `base.py`, model trong `models.py`, facade trong `api/`. **Không bao giờ** để `api/` import trực tiếp một provider cụ thể ngoài dòng `import ...providers.<src>  # noqa` để đăng ký.

---

## 1. Phạm vi mục tiêu — Build Matrix

Chỉ làm đúng các ô ✅ dưới đây (ánh xạ cột của doc gốc):

| Lớp (kind) | VCI | VND | MAS | CafeF | Method ưu tiên |
|---|:--:|:--:|:--:|:--:|---|
| **Listing** | ✅ | ✅ | – | – | `all_symbols`, `industry`, `symbols_by_exchange`, `symbols_by_group`, `symbols_by_industries` |
| **Quote** | ✅ | ✅ | ✅ | – | `history`, `intraday`, `price_depth` |
| **Company** | ✅ | – | – | – | `overview`, `shareholders`, `officers`, `subsidiaries`, `events`, `news`, `ratio_summary` |
| **Finance** | ✅ | ✅ | ✅ | – | `balance_sheet`, `income_statement`, `cashflow`, `ratio` (+`note` VCI, +`annual_plan` MAS) |
| **Trading** | ✅ | – | – | ✅ | VCI: `price_board`, `trading_stats`, `side_stats`; CafeF: `foreign_trade`, `prop_trade`, `order_stats`, `insider_deal` |
| **Market** | – | ✅ | – | – | `pe`, `pb`, `evaluation` |

Tổng cộng cần xây: **4 Lớp mới** (Company, Finance, Trading, Market) + **mở rộng 2 Lớp cũ** (Listing thêm method + nguồn VND; Quote thêm method intraday/price_depth + nguồn VND, MAS) + **3 nguồn mới** (VND, MAS, CafeF).

---

## 2. Models cần bổ sung (`core/models.py`)

Mỗi Lớp trả về `list[Model]`, facade tự `model_dump()` → DataFrame. Thiết kế model "phẳng" (flat) để ra DataFrame gọn.

```python
# Listing (đã có Symbol) — bổ sung tuỳ method:
class Industry(BaseModel):
    icb_code: str
    icb_name: str
    level: int

# Quote — đã có Bar (OHLCV). Thêm:
class Tick(BaseModel):           # intraday khớp lệnh
    symbol: str; time: datetime; price: float; volume: int; match_type: str | None = None
class PriceDepthLevel(BaseModel):  # price_depth
    symbol: str; price: float; bid_volume: int | None; ask_volume: int | None

# Company
class CompanyOverview(BaseModel):
    symbol: str; exchange: str | None; industry: str | None
    company_type: str | None; established_year: int | None
    listed_shares: int | None; website: str | None; outstanding_shares: int | None
class Shareholder(BaseModel):
    symbol: str; name: str; share_own: int | None; pct: float | None
class Officer(BaseModel):
    symbol: str; name: str; position: str | None; pct: float | None
class Subsidiary(BaseModel):
    symbol: str; name: str; ownership_pct: float | None
class CompanyEvent(BaseModel):
    symbol: str; event_name: str; ex_date: datetime | None; record_date: datetime | None
class NewsItem(BaseModel):
    symbol: str; title: str; published: datetime | None; source: str | None; url: str | None

# Finance — DÙNG MỘT MODEL CHUNG, "long format" để gộp đa nguồn dễ dàng:
class FinancialRow(BaseModel):
    symbol: str
    statement: str        # 'balance_sheet' | 'income_statement' | 'cashflow' | 'ratio'
    period: str           # '2024-Q1' | '2024' ...
    item_code: str | None # mã chỉ tiêu chuẩn hoá (nếu map được)
    item_name: str        # tên chỉ tiêu gốc
    value: float | None
    unit: str | None = "VND"
    parent_code: str | None = None  # phục vụ cấu trúc cha-con của MAS

# Trading
class PriceBoardRow(BaseModel):     # bảng giá realtime (VCI ~70 cột → rút gọn các trường lõi)
    symbol: str; ref: float | None; ceiling: float | None; floor: float | None
    match_price: float | None; match_volume: int | None
    bid1_price: float | None; bid1_volume: int | None
    ask1_price: float | None; ask1_volume: int | None
    foreign_buy: int | None; foreign_sell: int | None
class ForeignTrade(BaseModel):      # CafeF
    symbol: str; date: datetime; buy_volume: int | None; sell_volume: int | None
    buy_value: float | None; sell_value: float | None; net_value: float | None
class PropTrade(BaseModel):
    symbol: str; date: datetime; buy_value: float | None; sell_value: float | None
class OrderStat(BaseModel):
    symbol: str; date: datetime; buy_orders: int | None; sell_orders: int | None
    buy_volume: int | None; sell_volume: int | None
class InsiderDeal(BaseModel):
    symbol: str; person: str | None; action: str | None; volume: int | None; date: datetime | None

# Market (VND)
class ValuationPoint(BaseModel):
    symbol: str; date: datetime; metric: str  # 'pe' | 'pb'
    value: float | None
```

> **Quyết định thiết kế quan trọng — Finance dùng "long format":** vì VCI/VND/MAS trả cấu trúc rất khác (đặc biệt MAS phân cấp cha-con, dễ trùng tên cột), gộp về một bảng dài `(symbol, statement, period, item_name, value, parent_code)` giúp: (1) một model dùng cho cả 3 nguồn; (2) chuẩn hoá dần qua `item_code`; (3) người dùng tự `pivot` ra wide khi cần. Cung cấp helper `to_wide(df)` ở `api/financial.py`.

---

## 3. Chuẩn hoá đa nguồn (`core/normalize.py`) — lớp mới, then chốt

Cùng một Lớp, các nguồn trả tên trường khác nhau → cần map về schema model ở mục 2.

Thiết kế: mỗi provider khai báo một dict `FIELD_MAP` trong `const.py` của nó; `normalize.py` cung cấp hàm dùng chung.

```python
# core/normalize.py
def remap(raw: dict, field_map: dict[str, str]) -> dict:
    """Đổi key thô của nguồn -> tên field chuẩn của model. Bỏ qua key không map."""
    return {field_map[k]: v for k, v in raw.items() if k in field_map}

def to_float(x) -> float | None: ...   # xử lý '1,234.5', '', None, '-'
def to_int(x) -> int | None: ...
def parse_period(s, source) -> str: ...  # '2024Q1', 'Q1/2024' -> '2024-Q1'
```

Mỗi provider chỉ cần: `Model(**remap(raw_row, FIELD_MAP))`. Đây là điểm khiến việc thêm nguồn rất rẻ và là khác biệt chất lượng so với crawler rời rạc.

**Bảng map chỉ tiêu tài chính (quan trọng nhất):** tạo `providers/_shared/finance_items.py` chứa từ điển ánh xạ tên chỉ tiêu tiếng Việt của từng nguồn → `item_code` chuẩn (vd `TOTAL_ASSETS`, `NET_REVENUE`, `NET_PROFIT`, `ROE`, `ROA`...). Bắt đầu từ ~20–30 chỉ tiêu cốt lõi, mở rộng dần.

---

## 4. Kế hoạch theo từng Lớp (method · endpoint · nguồn)

Với mỗi Lớp: thêm ABC vào `providers/base.py`, model vào `models.py`, facade `api/<kind>.py`, rồi từng provider.

### 4.1. Listing — mở rộng (VCI + thêm VND)

ABC bổ sung method:
```python
class ListingProvider(ABC):
    @abstractmethod
    def all_symbols(self) -> list[Symbol]: ...
    # mới:
    def industry(self) -> list[Industry]: raise NotImplementedError
    def symbols_by_exchange(self, exchange: str) -> list[Symbol]: raise NotImplementedError
    def symbols_by_group(self, group: str) -> list[str]: raise NotImplementedError
    def symbols_by_industries(self) -> list[Symbol]: raise NotImplementedError
    # + bản _async tương ứng
```
> Dùng `raise NotImplementedError` (không `@abstractmethod`) cho method mở rộng để VND chỉ cần override `all_symbols` mà không vỡ. VCI override đầy đủ.

- **VCI**: `all_symbols`, `industry` (ICB), `symbols_by_exchange` (HOSE/HNX/UPCOM), `symbols_by_group` (VN30/VN100/HNX30), `symbols_by_industries`.
- **VND**: chỉ `all_symbols` (nhanh hơn, dùng fallback).

### 4.2. Quote — mở rộng (thêm `intraday`, `price_depth`; thêm VND, MAS)

```python
class QuoteProvider(ABC):
    @abstractmethod
    def history(self, symbol, start, end=None, interval="1D") -> list[Bar]: ...
    def intraday(self, symbol) -> list[Tick]: raise NotImplementedError
    def price_depth(self, symbol) -> list[PriceDepthLevel]: raise NotImplementedError
    # + _async
```
- **VCI**: `history` (đã có, bổ sung `interval` 1m–1M), `intraday`, `price_depth`.
- **VND**: `history` (nhanh, hỗ trợ 1m/5m/15m/30m), `intraday`, `price_depth` → là **nguồn fallback chính** cho OHLCV.
- **MAS**: `history` (giống VND, dùng khi 2 nguồn kia lỗi).

### 4.3. Company — Lớp mới (chỉ VCI)

```python
class CompanyProvider(ABC):
    @abstractmethod
    def overview(self, symbol) -> CompanyOverview: ...
    def shareholders(self, symbol) -> list[Shareholder]: raise NotImplementedError
    def officers(self, symbol) -> list[Officer]: raise NotImplementedError
    def subsidiaries(self, symbol) -> list[Subsidiary]: raise NotImplementedError
    def events(self, symbol) -> list[CompanyEvent]: raise NotImplementedError
    def news(self, symbol, mode="basic") -> list[NewsItem]: raise NotImplementedError
    def ratio_summary(self, symbol) -> list[FinancialRow]: raise NotImplementedError
    # + _async
```
Facade `api/company.py`: mỗi method trả DataFrame; `source="vci"` mặc định.

### 4.4. Finance — Lớp mới (VCI + VND + MAS)

```python
class FinanceProvider(ABC):
    @abstractmethod
    def balance_sheet(self, symbol, period="quarter") -> list[FinancialRow]: ...
    @abstractmethod
    def income_statement(self, symbol, period="quarter") -> list[FinancialRow]: ...
    @abstractmethod
    def cashflow(self, symbol, period="quarter") -> list[FinancialRow]: ...
    @abstractmethod
    def ratio(self, symbol, period="quarter") -> list[FinancialRow]: ...
    def note(self, symbol, period="quarter") -> list[FinancialRow]: raise NotImplementedError       # VCI
    def annual_plan(self, symbol) -> list[FinancialRow]: raise NotImplementedError                    # MAS
    # + _async
```
- **VCI**: 4 báo cáo + `note`; cấu trúc đơn giản → map thẳng.
- **VND**: 4 báo cáo cơ bản (ít chỉ tiêu hơn) → fallback.
- **MAS**: 4 báo cáo phân cấp cha-con (điền `parent_code`) + `annual_plan` (duy nhất MAS). **Lưu ý xử lý tên cột trùng** khi parse.

Facade `api/financial.py` thêm helper:
```python
def to_wide(df_long: pd.DataFrame) -> pd.DataFrame:
    return df_long.pivot_table(index="period", columns="item_name", values="value", aggfunc="first")
```

### 4.5. Trading — Lớp mới (VCI + CafeF)

```python
class TradingProvider(ABC):
    def price_board(self, symbols: list[str]) -> list[PriceBoardRow]: raise NotImplementedError   # VCI
    def trading_stats(self, symbol, start, end=None) -> list[...]: raise NotImplementedError       # VCI
    def side_stats(self, symbol, start, end=None) -> list[...]: raise NotImplementedError          # VCI
    def foreign_trade(self, symbol, start, end=None) -> list[ForeignTrade]: raise NotImplementedError  # CafeF
    def prop_trade(self, symbol, start, end=None) -> list[PropTrade]: raise NotImplementedError    # CafeF
    def order_stats(self, symbol, start, end=None) -> list[OrderStat]: raise NotImplementedError   # CafeF
    def insider_deal(self, symbol) -> list[InsiderDeal]: raise NotImplementedError                 # CafeF
    # + _async
```
- **VCI**: `price_board` (chọn lọc ~15 trường lõi từ 70 cột), `trading_stats`, `side_stats`.
- **CafeF**: `foreign_trade`, `prop_trade`, `order_stats`, `insider_deal`. ⚠️ API kém ổn định → retry + cache mạnh.

### 4.6. Market — Lớp mới (chỉ VND)

```python
class MarketProvider(ABC):
    @abstractmethod
    def pe(self, symbol="VNINDEX", start=None, end=None) -> list[ValuationPoint]: ...
    @abstractmethod
    def pb(self, symbol="VNINDEX", start=None, end=None) -> list[ValuationPoint]: ...
    def evaluation(self, symbol) -> list[ValuationPoint]: raise NotImplementedError
    # + _async
```

---

## 5. Ghi chú & "cạm bẫy" theo nguồn

| Nguồn | Lưu ý triển khai |
|---|---|
| **VCI** | Phủ rộng nhất nhưng **bị chặn dải IP** trên Google Colab/Kaggle → cần header browser-like + cho phép cấu hình proxy. BCTC khác cấu trúc MAS. |
| **VND** | Nhanh, ổn định → đặt làm **fallback OHLCV** và nguồn **duy nhất** cho Market (P/E, P/B). Ít method. |
| **MAS** | BCTC **phân cấp cha-con**, tên cột dễ trùng → parse cẩn thận, điền `parent_code`. Có `annual_plan` độc quyền. |
| **CafeF** | **API hay lỗi/đổi** → bọc retry, đánh dấu `experimental`, cache đĩa, test network tách riêng. |

**Nguyên tắc nhất quán dữ liệu (theo doc):** khuyến nghị người dùng chọn **1 nguồn chính** cho mỗi phân tích; chỉ fallback với dữ liệu đã chuẩn hoá (OHLCV). Không trộn BCTC từ 2 nguồn trong cùng một bảng.

---

## 6. Hạ tầng cần nâng cấp (làm cùng các Lớp)

1. **`core/cache.py`** — cache đĩa parquet theo khoá `(kind, source, symbol, params)`, TTL cấu hình. Giảm gọi API lặp (doc nhấn mạnh). Ưu tiên cho Finance/Company (ít đổi) và CafeF (hay lỗi).
2. **`core/client.py`** — bổ sung: timeout, **retry + backoff**, **rate-limit** (token bucket), xoay `User-Agent`, hook proxy. Đây là nền cho VCI/CafeF.
3. **`core/exceptions.py`** — thêm `RateLimitError`, `SymbolNotFound`, `SourceUnavailable`.
4. **Fallback helper** — `api/_fallback.py`:
   ```python
   def with_fallback(fn, sources, *args, **kwargs):
       for s in sources:
           try: return fn(*args, source=s, **kwargs)
           except SourceError: continue
       raise SourceError(f"Tất cả nguồn {sources} đều lỗi")
   ```
   Áp dụng cho Quote/Listing (đã chuẩn hoá). Thứ tự ưu tiên OHLCV: `["vnd", "vci", "mas"]`.
5. **Validation** — sau parse, kiểm tra logic OHLC (`high>=low`, `high>=open/close`...), loại dòng rác.

---

## 7. Chiến lược test

- **Fixtures JSON** cho từng endpoint × nguồn trong `tests/fixtures/<source>/<method>.json` (lưu 1 response thật đã rút gọn).
- **Unit test** dùng `respx` mock HTTP → kiểm tra parse/normalize ra đúng model & DataFrame (không chạm mạng).
- **Integration test** đánh dấu `@pytest.mark.network`, chạy thủ công/cron (đã cấu hình `-m 'not network'` trong CI) → phát hiện nguồn đổi cấu trúc.
- **Test normalize**: bảng map chỉ tiêu tài chính có test riêng (đầu vào tên VN → `item_code`).
- Mục tiêu coverage ≥ 80% (loại phần network).
- Thêm workflow cron `data-health.yml` chạy integration hằng ngày, mở issue khi nguồn hỏng (học từ vnstock `verify-api-key`/`performance`).

---

## 8. Roadmap phiên bản

| Version | Nội dung | Lý do thứ tự |
|---|---|---|
| **v0.2** | Listing đầy đủ (VCI: industry, by_exchange, by_group, by_industries) + VND `all_symbols` + Quote `intraday`/`price_depth` (VCI) + nâng cấp `client` (retry/rate-limit) | Hoàn thiện 2 Lớp đã có; dựng hạ tầng dùng chung |
| **v0.3** | **Company (VCI)** đầy đủ + `core/cache.py` | Dữ liệu ít đổi, hợp để khởi động cache |
| **v0.4** | **Finance** long-format: VCI 4 báo cáo + `note`; `to_wide()`; bảng map chỉ tiêu cốt lõi | Lớp giá trị cao nhất cho phân tích cơ bản |
| **v0.5** | Finance thêm **VND** + **MAS** (cha-con, `annual_plan`) + Quote thêm VND/MAS + fallback helper | Đa nguồn, kiểm chứng normalize |
| **v0.6** | **Trading**: VCI (`price_board`, `trading_stats`, `side_stats`) | Realtime/board, cần rate-limit ổn |
| **v0.7** | **Trading CafeF** (foreign/prop/order/insider) + **Market VND** (pe/pb/evaluation) | Nguồn kém ổn định để sau; Market gọn |

> Sau mỗi version: cập nhật README matrix, CHANGELOG (Keep a Changelog), bump SemVer, publish TestPyPI → PyPI.

---

## 9. Checklist tổng (theo đầu việc)

**Hạ tầng (làm sớm, v0.2)**
- [ ] Nâng cấp `HttpClient`: timeout, retry/backoff, rate-limit, UA rotation, proxy hook
- [ ] `core/normalize.py` (`remap`, `to_float/int`, `parse_period`)
- [ ] Bổ sung exceptions: `RateLimitError`, `SymbolNotFound`, `SourceUnavailable`
- [ ] `core/cache.py` (parquet, TTL)
- [ ] `api/_fallback.py`

**Models (`core/models.py`)**
- [ ] Industry, Tick, PriceDepthLevel
- [ ] CompanyOverview, Shareholder, Officer, Subsidiary, CompanyEvent, NewsItem
- [ ] FinancialRow (long format) + `providers/_shared/finance_items.py`
- [ ] PriceBoardRow, ForeignTrade, PropTrade, OrderStat, InsiderDeal
- [ ] ValuationPoint

**Lớp × Nguồn (mỗi ô = 1 file provider + đăng ký + test)**
- [ ] Listing: VCI (industry, by_exchange, by_group, by_industries), VND (all_symbols)
- [ ] Quote: VCI (intraday, price_depth, interval), VND (history/intraday/price_depth), MAS (history)
- [ ] Company: VCI (overview, shareholders, officers, subsidiaries, events, news, ratio_summary)
- [ ] Finance: VCI (4+note), VND (4), MAS (4+annual_plan)
- [ ] Trading: VCI (price_board, trading_stats, side_stats), CafeF (foreign_trade, prop_trade, order_stats, insider_deal)
- [ ] Market: VND (pe, pb, evaluation)

**Facade `api/`**
- [ ] company.py, financial.py (+`to_wide`), trading.py, market.py
- [ ] cập nhật `__init__.py` export 4 Lớp mới

**Chất lượng**
- [ ] Fixtures + unit test (respx) cho mọi method
- [ ] Integration `@pytest.mark.network` + workflow cron `data-health.yml`
- [ ] Cập nhật README matrix + CHANGELOG + docs ví dụ

---

## 10. Bắt đầu từ đâu (gợi ý 1 tuần đầu)

1. Nâng cấp `HttpClient` (retry + rate-limit) — nền cho mọi nguồn.
2. Thêm `core/normalize.py` + viết test cho nó.
3. Hoàn thiện **Listing VCI** (4 method còn lại) làm mẫu pattern "method mở rộng + normalize".
4. Thêm **VND provider** cho `Listing.all_symbols` + `Quote.history` → kiểm chứng đa nguồn + fallback.
5. Release v0.2, rồi đi tiếp Company (v0.3).
```
```
*Pháp lý: chỉ truy cập API công khai, không phân phối lại dữ liệu thô; giữ disclaimer "không phải khuyến nghị đầu tư". Không sao chép mã nguồn vnstock (license phi thương mại) — tự viết lại.*
