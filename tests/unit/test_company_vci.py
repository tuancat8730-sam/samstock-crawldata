import pytest
import respx
from httpx import Response

from samvnstock.providers.vci.company import VciCompanyProvider
from samvnstock.providers.vci.const import (
    COMPANY_EVENTS_URL,
    COMPANY_NEWS_URL,
    VCI_COMPANY_URL,
)

_DETAILS_RESPONSE = {
    "data": {
        "ticker": "VCB",
        "viOrganName": "Ngân hàng TMCP Ngoại thương Việt Nam",
        "viOrganShortName": "Vietcombank",
        "sectorVn": "Ngân hàng",
        "profile": "<p>Vietcombank là...</p>",
        "listingDate": "2009-06-30",
        "numberOfSharesMktCap": "5,589,072,002",
    }
}

_SHAREHOLDER_LIST_RESPONSE = {
    "data": [
        {
            "ownerName": "State Bank of Vietnam",
            "percentage": 74.8,
            "quantity": 4180000000,
            "updateDate": 1704067200000,
            "ownerType": "ORGANIZATION",
            "positionName": None,
        },
        {
            "ownerName": "Nguyễn Văn A",
            "percentage": 0.01,
            "quantity": 500000,
            "updateDate": 1704067200000,
            "ownerType": "INDIVIDUAL",
            "positionName": "Tổng Giám đốc",
        },
    ]
}

_RELATIONSHIP_RESPONSE = {
    "data": {
        "subsidiaries": [
            {"rightOrganNameVi": "Công ty Con A", "rightOrganCode": "CA", "ownedPercentage": 100.0}
        ],
        "affiliates": [
            {
                "rightOrganNameVi": "Công ty Liên kết B",
                "rightOrganCode": "CB",
                "ownedPercentage": 30.0,
            }
        ],
    }
}

_EVENTS_RESPONSE = {
    "data": {
        "content": [
            {
                "eventTitle": "Trả cổ tức bằng tiền",
                "eventCode": "DIV",
                "publicDate": "2024-05-01",
                "recordDate": "2024-05-10",
                "exrightDate": "2024-05-09",
            }
        ]
    }
}

_NEWS_RESPONSE = {
    "data": {
        "content": [
            {"title": "VCB báo lãi kỷ lục", "publicDate": "2024-04-01", "newsSource": "CafeF"}
        ]
    }
}

_RATIO_SUMMARY_RESPONSE = {"data": {"pe": 15.2, "pb": 2.1, "roe": "18.5", "__typename": "Ratio"}}


@respx.mock
def test_overview_parses_company_details() -> None:
    respx.get(f"{VCI_COMPANY_URL}/details").mock(return_value=Response(200, json=_DETAILS_RESPONSE))

    overview = VciCompanyProvider().overview("VCB")

    assert overview.symbol == "VCB"
    assert overview.organ_short_name == "Vietcombank"
    assert overview.issue_share == 5589072002


@pytest.mark.asyncio
@respx.mock
async def test_overview_async_matches_sync() -> None:
    respx.get(f"{VCI_COMPANY_URL}/details").mock(return_value=Response(200, json=_DETAILS_RESPONSE))

    overview = await VciCompanyProvider().overview_async("VCB")

    assert overview.symbol == "VCB"


@respx.mock
def test_shareholders_parses_list_and_normalizes_update_date() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/shareholder").mock(
        return_value=Response(200, json=_SHAREHOLDER_LIST_RESPONSE)
    )

    rows = VciCompanyProvider().shareholders("VCB")

    assert len(rows) == 2
    assert rows[0].share_holder == "State Bank of Vietnam"
    assert rows[0].update_date == "2024-01-01"


@respx.mock
def test_officers_filters_individuals_with_position() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/shareholder").mock(
        return_value=Response(200, json=_SHAREHOLDER_LIST_RESPONSE)
    )

    rows = VciCompanyProvider().officers("VCB")

    assert len(rows) == 1
    assert rows[0].officer_name == "Nguyễn Văn A"
    assert rows[0].officer_position == "Tổng Giám đốc"


@respx.mock
def test_subsidiaries_combines_subsidiary_and_affiliate() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/relationship").mock(
        return_value=Response(200, json=_RELATIONSHIP_RESPONSE)
    )

    rows = VciCompanyProvider().subsidiaries("VCB")

    assert len(rows) == 2
    assert {r.type for r in rows} == {"subsidiary", "affiliate"}


@respx.mock
def test_events_parses_content_with_best_effort_title() -> None:
    respx.get(COMPANY_EVENTS_URL).mock(return_value=Response(200, json=_EVENTS_RESPONSE))

    rows = VciCompanyProvider().events("VCB")

    assert len(rows) == 1
    assert rows[0].event_title == "Trả cổ tức bằng tiền"
    assert rows[0].event_code == "DIV"


@respx.mock
def test_news_parses_content() -> None:
    respx.get(COMPANY_NEWS_URL).mock(return_value=Response(200, json=_NEWS_RESPONSE))

    rows = VciCompanyProvider().news("VCB")

    assert len(rows) == 1
    assert rows[0].title == "VCB báo lãi kỷ lục"
    assert rows[0].source == "CafeF"


@respx.mock
def test_ratio_summary_flattens_to_long_format() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/statistics-financial").mock(
        return_value=Response(200, json=_RATIO_SUMMARY_RESPONSE)
    )

    rows = VciCompanyProvider().ratio_summary("VCB")

    by_name = {r.item_name: r.value for r in rows}
    assert by_name["pe"] == 15.2
    assert by_name["roe"] == 18.5
    assert "__typename" not in by_name


@pytest.mark.asyncio
@respx.mock
async def test_shareholders_async_matches_sync() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/shareholder").mock(
        return_value=Response(200, json=_SHAREHOLDER_LIST_RESPONSE)
    )

    rows = await VciCompanyProvider().shareholders_async("VCB")

    assert len(rows) == 2


@pytest.mark.asyncio
@respx.mock
async def test_officers_async_matches_sync() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/shareholder").mock(
        return_value=Response(200, json=_SHAREHOLDER_LIST_RESPONSE)
    )

    rows = await VciCompanyProvider().officers_async("VCB")

    assert len(rows) == 1


@pytest.mark.asyncio
@respx.mock
async def test_subsidiaries_async_matches_sync() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/relationship").mock(
        return_value=Response(200, json=_RELATIONSHIP_RESPONSE)
    )

    rows = await VciCompanyProvider().subsidiaries_async("VCB")

    assert len(rows) == 2


@pytest.mark.asyncio
@respx.mock
async def test_events_async_matches_sync() -> None:
    respx.get(COMPANY_EVENTS_URL).mock(return_value=Response(200, json=_EVENTS_RESPONSE))

    rows = await VciCompanyProvider().events_async("VCB")

    assert len(rows) == 1


@pytest.mark.asyncio
@respx.mock
async def test_news_async_matches_sync() -> None:
    respx.get(COMPANY_NEWS_URL).mock(return_value=Response(200, json=_NEWS_RESPONSE))

    rows = await VciCompanyProvider().news_async("VCB")

    assert len(rows) == 1


@pytest.mark.asyncio
@respx.mock
async def test_ratio_summary_async_matches_sync() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/statistics-financial").mock(
        return_value=Response(200, json=_RATIO_SUMMARY_RESPONSE)
    )

    rows = await VciCompanyProvider().ratio_summary_async("VCB")

    assert len(rows) == 3
