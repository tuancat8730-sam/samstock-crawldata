import respx
from httpx import Response

import samvnstock
from samvnstock.providers.vci.const import COMPANY_EVENTS_URL, COMPANY_NEWS_URL, VCI_COMPANY_URL

_SHAREHOLDER_LIST_RESPONSE = {
    "data": [
        {
            "ownerName": "State Bank of Vietnam",
            "percentage": 74.8,
            "quantity": 4180000000,
            "updateDate": "2024-01-01",
            "ownerType": "ORGANIZATION",
            "positionName": None,
        }
    ]
}

_RELATIONSHIP_RESPONSE = {
    "data": {
        "subsidiaries": [
            {"rightOrganNameVi": "Công ty Con A", "rightOrganCode": "CA", "ownedPercentage": 100.0}
        ],
        "affiliates": [],
    }
}

_EVENTS_RESPONSE = {"data": {"content": [{"eventTitle": "Trả cổ tức", "publicDate": "2024-05-01"}]}}
_NEWS_RESPONSE = {"data": {"content": [{"title": "Tin VCB", "publicDate": "2024-04-01"}]}}
_RATIO_SUMMARY_RESPONSE = {"data": {"pe": 15.2}}

_DETAILS_RESPONSE = {
    "data": {
        "ticker": "VCB",
        "viOrganName": "Ngân hàng TMCP Ngoại thương Việt Nam",
        "viOrganShortName": "Vietcombank",
        "sectorVn": "Ngân hàng",
        "listingDate": "2009-06-30",
        "numberOfSharesMktCap": 5589072002,
    }
}


@respx.mock
def test_overview_returns_dataframe() -> None:
    respx.get(f"{VCI_COMPANY_URL}/details").mock(return_value=Response(200, json=_DETAILS_RESPONSE))

    df = samvnstock.company.overview("VCB")

    assert df.iloc[0]["organ_short_name"] == "Vietcombank"


@respx.mock
def test_overview_with_cache_avoids_second_http_call(tmp_path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from samvnstock.api import company as company_module
    from samvnstock.core.cache import ParquetCache

    monkeypatch.setattr(company_module, "_cache", ParquetCache(cache_dir=tmp_path))
    route = respx.get(f"{VCI_COMPANY_URL}/details").mock(
        return_value=Response(200, json=_DETAILS_RESPONSE)
    )

    df1 = samvnstock.company.overview("VCB", use_cache=True)
    df2 = samvnstock.company.overview("VCB", use_cache=True)

    assert route.call_count == 1
    assert df1.iloc[0]["organ_short_name"] == df2.iloc[0]["organ_short_name"]


@respx.mock
async def test_overview_async_returns_dataframe() -> None:
    respx.get(f"{VCI_COMPANY_URL}/details").mock(return_value=Response(200, json=_DETAILS_RESPONSE))

    df = await samvnstock.company.overview_async("VCB")

    assert df.iloc[0]["symbol"] == "VCB"


@respx.mock
def test_shareholders_officers_subsidiaries_return_dataframes() -> None:
    respx.get(f"{VCI_COMPANY_URL}/VCB/shareholder").mock(
        return_value=Response(200, json=_SHAREHOLDER_LIST_RESPONSE)
    )
    respx.get(f"{VCI_COMPANY_URL}/VCB/relationship").mock(
        return_value=Response(200, json=_RELATIONSHIP_RESPONSE)
    )

    assert samvnstock.company.shareholders("VCB").iloc[0]["share_holder"] == "State Bank of Vietnam"
    assert samvnstock.company.subsidiaries("VCB").iloc[0]["organ_name"] == "Công ty Con A"


@respx.mock
def test_events_news_ratio_summary_return_dataframes() -> None:
    respx.get(COMPANY_EVENTS_URL).mock(return_value=Response(200, json=_EVENTS_RESPONSE))
    respx.get(COMPANY_NEWS_URL).mock(return_value=Response(200, json=_NEWS_RESPONSE))
    respx.get(f"{VCI_COMPANY_URL}/VCB/statistics-financial").mock(
        return_value=Response(200, json=_RATIO_SUMMARY_RESPONSE)
    )

    assert samvnstock.company.events("VCB").iloc[0]["event_title"] == "Trả cổ tức"
    assert samvnstock.company.news("VCB").iloc[0]["title"] == "Tin VCB"
    assert samvnstock.company.ratio_summary("VCB").iloc[0]["item_name"] == "pe"
