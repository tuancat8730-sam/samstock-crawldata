import respx
from httpx import Response

import samvnstock
from samvnstock.api.financial import to_wide
from samvnstock.providers.vci.const import VCI_COMPANY_URL

_METRICS_RESPONSE = {
    "data": {
        "BALANCE_SHEET": [
            {"field": "totalAssets", "parent": None, "titleVi": "Tổng tài sản"},
        ]
    }
}

_BALANCE_SHEET_RESPONSE = {
    "data": {
        "quarters": [
            {"yearReport": 2024, "lengthReport": 1, "totalAssets": 1500000},
            {"yearReport": 2023, "lengthReport": 4, "totalAssets": 1400000},
        ],
        "years": [],
    }
}

_RATIO_RESPONSE = {"data": [{"year": 2024, "quarter": 1, "pe": 15.2}]}


@respx.mock
def test_balance_sheet_returns_long_format_dataframe() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement").mock(
        return_value=Response(200, json=_BALANCE_SHEET_RESPONSE)
    )
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement/metrics").mock(
        return_value=Response(200, json=_METRICS_RESPONSE)
    )

    df = samvnstock.financial.balance_sheet("VCB", period="quarter")

    assert list(df.columns) == [
        "symbol",
        "statement",
        "period",
        "item_code",
        "item_name",
        "value",
        "unit",
        "parent_code",
    ]
    assert len(df) == 2


@respx.mock
def test_to_wide_pivots_period_by_item_name() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement").mock(
        return_value=Response(200, json=_BALANCE_SHEET_RESPONSE)
    )
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement/metrics").mock(
        return_value=Response(200, json=_METRICS_RESPONSE)
    )

    df_long = samvnstock.financial.balance_sheet("VCB", period="quarter")
    df_wide = to_wide(df_long)

    assert df_wide.loc["2024-Q1", "Tổng tài sản"] == 1500000
    assert df_wide.loc["2023-Q4", "Tổng tài sản"] == 1400000


@respx.mock
def test_balance_sheet_with_cache_avoids_second_http_call(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from samvnstock.api import financial as financial_module
    from samvnstock.core.cache import ParquetCache

    monkeypatch.setattr(financial_module, "_cache", ParquetCache(cache_dir=tmp_path))
    route = respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement").mock(
        return_value=Response(200, json=_BALANCE_SHEET_RESPONSE)
    )
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement/metrics").mock(
        return_value=Response(200, json=_METRICS_RESPONSE)
    )

    samvnstock.financial.balance_sheet("VCB", use_cache=True)
    samvnstock.financial.balance_sheet("VCB", use_cache=True)

    assert route.call_count == 1


@respx.mock
def test_ratio_returns_dataframe() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/statistics-financial").mock(
        return_value=Response(200, json=_RATIO_RESPONSE)
    )

    df = samvnstock.financial.ratio("VCB")

    assert df.iloc[0]["item_code"] == "PE"


@respx.mock
async def test_balance_sheet_async_returns_dataframe() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement").mock(
        return_value=Response(200, json=_BALANCE_SHEET_RESPONSE)
    )
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement/metrics").mock(
        return_value=Response(200, json=_METRICS_RESPONSE)
    )

    df = await samvnstock.financial.balance_sheet_async("VCB")

    assert len(df) == 2


@respx.mock
async def test_income_statement_cashflow_ratio_async_return_dataframes() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement").mock(
        return_value=Response(200, json=_BALANCE_SHEET_RESPONSE)
    )
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement/metrics").mock(
        return_value=Response(200, json=_METRICS_RESPONSE)
    )
    respx.get(f"{VCI_COMPANY_URL}/VCB/statistics-financial").mock(
        return_value=Response(200, json=_RATIO_RESPONSE)
    )

    assert len(await samvnstock.financial.income_statement_async("VCB")) == 2
    assert len(await samvnstock.financial.cashflow_async("VCB")) == 2
    assert len(await samvnstock.financial.ratio_async("VCB")) == 1
