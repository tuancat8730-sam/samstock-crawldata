import pytest
import respx
from httpx import Response

from samvnstock.providers.vci.const import VCI_COMPANY_URL
from samvnstock.providers.vci.finance import VciFinanceProvider

_METRICS_RESPONSE = {
    "data": {
        "BALANCE_SHEET": [
            {
                "field": "totalAssets",
                "parent": None,
                "titleVi": "Tổng tài sản",
                "titleEn": "Total Assets",
            },
            {
                "field": "currentAssets",
                "parent": "totalAssets",
                "titleVi": "Tài sản ngắn hạn",
                "titleEn": "Current Assets",
            },
        ]
    }
}

_BALANCE_SHEET_RESPONSE = {
    "data": {
        "quarters": [
            {
                "yearReport": 2024,
                "lengthReport": 1,
                "totalAssets": 1500000,
                "currentAssets": 600000,
            },
            {
                "yearReport": 2023,
                "lengthReport": 4,
                "totalAssets": 1400000,
                "currentAssets": 550000,
            },
        ],
        "years": [
            {
                "yearReport": 2023,
                "lengthReport": 5,
                "totalAssets": 1400000,
                "currentAssets": 550000,
            },
        ],
    }
}

_RATIO_RESPONSE = {
    "data": [
        {"year": 2024, "quarter": 1, "pe": 15.2, "pb": 2.1, "roe": 18.5, "unknownField": "x"},
    ]
}


@respx.mock
def test_balance_sheet_parses_quarter_rows_with_parent_code() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement").mock(
        return_value=Response(200, json=_BALANCE_SHEET_RESPONSE)
    )
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement/metrics").mock(
        return_value=Response(200, json=_METRICS_RESPONSE)
    )

    rows = VciFinanceProvider().balance_sheet("VCB", period="quarter")

    assert len(rows) == 4
    by_period = {(r.period, r.item_code): r for r in rows}
    row = by_period[("2024-Q1", "currentAssets")]
    assert row.value == 600000
    assert row.parent_code == "totalAssets"
    assert row.item_name == "Tài sản ngắn hạn"


@respx.mock
def test_balance_sheet_uses_years_key_when_period_is_year() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement").mock(
        return_value=Response(200, json=_BALANCE_SHEET_RESPONSE)
    )
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement/metrics").mock(
        return_value=Response(200, json=_METRICS_RESPONSE)
    )

    rows = VciFinanceProvider().balance_sheet("VCB", period="year")

    assert len(rows) == 2
    assert all(r.period == "2023" for r in rows)


@pytest.mark.asyncio
@respx.mock
async def test_balance_sheet_async_matches_sync() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement").mock(
        return_value=Response(200, json=_BALANCE_SHEET_RESPONSE)
    )
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement/metrics").mock(
        return_value=Response(200, json=_METRICS_RESPONSE)
    )

    rows = await VciFinanceProvider().balance_sheet_async("VCB", period="quarter")

    assert len(rows) == 4


@respx.mock
def test_income_statement_and_cashflow_use_correct_section() -> None:
    income_route = respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement").mock(
        return_value=Response(200, json=_BALANCE_SHEET_RESPONSE)
    )
    respx.get(f"{VCI_COMPANY_URL}/VCB/financial-statement/metrics").mock(
        return_value=Response(200, json=_METRICS_RESPONSE)
    )

    VciFinanceProvider().income_statement("VCB")
    VciFinanceProvider().cashflow("VCB")

    assert income_route.calls[0].request.url.params["section"] == "INCOME_STATEMENT"
    assert income_route.calls[1].request.url.params["section"] == "CASH_FLOW"


@respx.mock
def test_ratio_maps_known_fields_and_skips_unknown() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/statistics-financial").mock(
        return_value=Response(200, json=_RATIO_RESPONSE)
    )

    rows = VciFinanceProvider().ratio("VCB", period="quarter")

    by_code = {r.item_code: r for r in rows}
    assert by_code["PE"].value == 15.2
    assert by_code["PE"].period == "2024-Q1"
    assert "unknownField" not in by_code
    assert len(rows) == 3


@pytest.mark.asyncio
@respx.mock
async def test_ratio_async_matches_sync() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/statistics-financial").mock(
        return_value=Response(200, json=_RATIO_RESPONSE)
    )

    rows = await VciFinanceProvider().ratio_async("VCB")

    assert len(rows) == 3
