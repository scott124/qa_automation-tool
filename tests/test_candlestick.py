import pytest
import json
import allure
from api.candlestick_api import CandlestickAPI
from jsonschema import validate
from utils.schemas import candlestick_schema


with open("data/candlestick_testdata.json", encoding="utf-8") as f:
    cases = json.load(f)

@allure.feature("Public API - Candlestick(測試用API)")
@pytest.mark.smoke
@pytest.mark.parametrize("case", cases, ids=[c["desc"] for c in cases])
def test_get_candlestick(case, env):
    api = CandlestickAPI(env=env)
    with allure.step("呼叫 {env} 環境 get-candlestick API"):
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
            
    # UAT環境驗證，原因是返回值為固定值，若正式環境這段可拿掉。
    for i, kline in enumerate(data):
        for key in ["o", "h", "l", "c", "v", "t"]:
            assert key in kline, f"[{i}] 缺少欄位: {key}"

        if "expected_open" in case:
            assert kline["o"] == case["expected_open"], f"[{i}] 預期開盤價格:{case['expected_open']}，實際開盤價格:{kline['o']}"
        if "expected_high" in case:
            assert kline["h"] == case["expected_high"], f"[{i}] 預期最高價:{case['expected_high']}，實際:{kline['h']}"
        if "expected_low" in case:
            assert kline["l"] == case["expected_low"], f"[{i}] 預期最低價:{case['expected_low']}，實際:{kline['l']}"
        if "expected_close" in case:
            assert kline["c"] == case["expected_close"], f"[{i}] 預期收盤價:{case['expected_close']}，實際:{kline['c']}"
        if "expected_volume" in case:
            assert kline["v"] == case["expected_volume"], f"[{i}] 預期交易量:{case['expected_volume']}，實際:{kline['v']}"
        if "expected_ts" in case:
            assert kline["t"] == case["expected_ts"], f"[{i}] 預期時間戳:{case['expected_ts']}，實際:{kline['t']}"
    else:
        with allure.step("異常或無數據情境"):
            data = resp_json.get("result", {}).get("data", [])
            # UAV預設值
            DEFAULT_O = "106816.0"
            DEFAULT_H = "106816.0"
            DEFAULT_L = "106816.0"
            DEFAULT_C = "106816.0"
            DEFAULT_V = "0"

            # 全部都是預設UAT假資料就算通過
            all_default = all(
                k["o"] == DEFAULT_O and
                k["h"] == DEFAULT_H and
                k["l"] == DEFAULT_L and
                k["c"] == DEFAULT_C and
                k["v"] == DEFAULT_V
                for k in data
            )
            assert resp_json["code"] != 0 or not data or all_default, f"異常場景 data: {data}"