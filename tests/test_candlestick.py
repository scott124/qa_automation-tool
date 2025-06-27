import pytest
import json
import allure
from api.candlestick_api import CandlestickAPI
from jsonschema import validate
from utils.schemas import candlestick_schema
from utils.timeframe import TIMEFRAME_TO_INTERVAL


with open("data/candlestick_testdata.json", encoding="utf-8") as f:
    cases = json.load(f)

@allure.feature("Public API - Candlestick(測試用API)")
@pytest.mark.smoke
@pytest.mark.parametrize("case", cases, ids=[c["desc"] for c in cases])
def test_get_candlestick(case, env):
    api = CandlestickAPI(env=env)
    with allure.step(f"呼叫 {env} 環境 get-candlestick API"):
        resp = api.get_candlestick(
            instrument_name=case["instrument_name"],
            timeframe=case["timeframe"]
        )
    with allure.step("驗證 HTTP code 200"):
        assert resp.status_code == 200, f"實際: {resp.status_code}, 預期: 200"
        
    resp_json = resp.json()
    
    with allure.step("驗證回應格式"):
        assert "code" in resp_json
        assert resp_json["code"] == case["expected_code"]
        assert resp_json["method"] == "public/get-candlestick"
    
    with allure.step("Schema 驗證"):
        validate(instance=resp_json, schema=candlestick_schema)  
        
    if case.get("expect_data", False) and resp_json["code"] == 0:
        with allure.step("驗證數據陣列&內容"):
            data = resp_json["result"]["data"]
            assert isinstance(data, list), "data 不是 list"
            assert len(data) > 0, "data 陣列為空"
            
            for i, kline in enumerate(data):
                for key in ["o", "h", "l", "c", "v", "t"]:
                    assert key in kline, f"[{i}] 缺少欄位: {key}"
                try:
                    o, h, l, c = map(float, [kline["o"], kline["h"], kline["l"], kline["c"]])
                    v = float(kline["v"])
                    assert h >= l, f"[{i}] high({h}) < low({l})" #驗證高價>=低價
                    assert h >= o and h >= c and h >= l #驗證高價>=低價、開盤價、收盤價
                    assert l <= o and l <= c and l <= h #驗證低價<=開盤價、收盤價、高價
                    assert v >= 0, f"[{i}] 交易量<0: {v}" #驗證交易量>=0
                except Exception as e:
                    assert False, f"[{i}] 數值轉換/邏輯異常: {e}"
