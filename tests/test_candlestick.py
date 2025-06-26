import pytest
import json
import allure
from api.candlestick_api import CandlestickAPI

with open("data/candlestick_testdata.json", encoding="utf-8") as f:
    cases = json.load(f)

@allure.feature("Public API - Candlestick")
@pytest.mark.parametrize("case", cases, ids=[c["desc"] for c in cases])
def test_get_candlestick(case):
    api = CandlestickAPI()
    with allure.step("呼叫 get-candlestick API"):
        resp = api.get_candlestick(
            instrument_name=case["instrument_name"],
            timeframe=case["timeframe"]
        )
    with allure.step("驗證 HTTP code"):
        assert resp.status_code == 200
    resp_json = resp.json()
    with allure.step("驗證回應格式"):
        assert "code" in resp_json
        assert resp_json["code"] == case["expected_code"]
        assert resp_json["method"] == "public/get-candlestick"
    if case.get("expect_data", False) and resp_json["code"] == 0:
        with allure.step("驗證數據陣列&內容"):
            assert "data" in resp_json["result"]
            assert isinstance(resp_json["result"]["data"], list)
    else:
        with allure.step("異常或無數據情境"):
            assert resp_json["code"] != 0 or not resp_json.get("result", {}).get("data", [])
