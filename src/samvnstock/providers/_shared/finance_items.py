"""Standardized item codes for financial ratios, shared across Finance sources.

Each entry maps a source's raw field key (e.g. VCI's `pe`) to a
`(item_code, item_name_vi)` pair. Starting with ~25 core ratios per
[[KE-HOACH-CRAWL-DATA-CHI-TIET-1]] section 3; extend as more sources/ratios
are added rather than mapping every possible field up front.
"""

VCI_RATIO_ITEM_MAP: dict[str, tuple[str, str]] = {
    "pe": ("PE", "P/E"),
    "pb": ("PB", "P/B"),
    "ps": ("PS", "P/S"),
    "roe": ("ROE", "ROE (%)"),
    "roa": ("ROA", "ROA (%)"),
    "roic": ("ROIC", "ROIC (%)"),
    "grossMargin": ("GROSS_MARGIN", "Biên lợi nhuận gộp (%)"),
    "ebitMargin": ("EBIT_MARGIN", "Biên EBIT (%)"),
    "afterTaxProfitMargin": ("NET_MARGIN", "Biên lợi nhuận sau thuế (%)"),
    "debtToEquity": ("DEBT_TO_EQUITY", "Nợ/Vốn chủ sở hữu"),
    "currentRatio": ("CURRENT_RATIO", "Hệ số thanh toán hiện hành"),
    "quickRatio": ("QUICK_RATIO", "Hệ số thanh toán nhanh"),
    "cashRatio": ("CASH_RATIO", "Hệ số thanh toán tiền mặt"),
    "dividendYield": ("DIVIDEND_YIELD", "Tỷ suất cổ tức (%)"),
    "marketCap": ("MARKET_CAP", "Vốn hóa thị trường"),
    "ownersEquity": ("OWNERS_EQUITY", "Vốn chủ sở hữu"),
    "ebitda": ("EBITDA", "EBITDA"),
    "ebit": ("EBIT", "EBIT"),
    "evToEbitda": ("EV_EBITDA", "EV/EBITDA"),
    "priceToCashFlow": ("PRICE_TO_CASH_FLOW", "Giá/Dòng tiền"),
    "assetTurnover": ("ASSET_TURNOVER", "Vòng quay tài sản"),
    "financialLeverage": ("FINANCIAL_LEVERAGE", "Đòn bẩy tài chính"),
    "npl": ("NPL", "Tỷ lệ nợ xấu (%)"),
    "car": ("CAR", "Hệ số an toàn vốn (%)"),
    "casaRatio": ("CASA_RATIO", "Tỷ lệ CASA (%)"),
    "numberOfSharesMktCap": ("OUTSTANDING_SHARES", "Số lượng cổ phiếu lưu hành"),
}
