import pytest
import json
import allure
from api.candlestick_api import CandlestickAPI
from jsonschema import validate
from schema.candlestick_schema import candlestick_schema
from utils.timeframe import TIMEFRAME_TO_INTERVAL

with open("data/candlestick_testdata.json", encoding="utf-8") as f:
    cases = json.load(f)

# cases = [c for c in cases if c["desc"] == "count為負數"] #測單一一筆可以這樣寫

@allure.feature("API - Candlestick")
@pytest.mark.api
@pytest.mark.parametrize("case", cases, ids=[c["desc"] for c in cases])
def test_get_candlestick(case, env):
    api = CandlestickAPI(env=env)
    with allure.step(f"呼叫 {env} 環境 get-candlestick API"):
        try:
            resp = api.get_candlestick(
                instrument_name=case["instrument_name"],
                timeframe=case.get("timeframe"),
                count=case.get("count")
            )
            resp.raise_for_status()
        except Exception as e:
            # 捕獲 HTTPError 取回 response（讓異常測資可繼續驗證）
            resp = getattr(e, "response", None)
            assert resp is not None, f"未取得 response，錯誤: {e}"

    with allure.step("驗證 HTTP code 200 or 異常環境"):
        if case.get("expect_data", False):
            # 正常情境需驗證 HTTP code=200
            assert resp.status_code == 200, f"實際: {resp.status_code}, 預期: 200"
        else:
            # 非預期資料時，允許 HTTP code 是 4xx/5xx
            assert 400 <= resp.status_code < 600, f"異常測資預期 4xx/5xx，實際: {resp.status_code}"

    resp_json = resp.json()

    with allure.step("驗證回應格式"):
        # 所有情境都要有 code
        assert "code" in resp_json
        assert resp_json["code"] == case["expected_code"]
        if "expected_message" in case:
            assert resp_json.get("message", "") == case["expected_message"]
        if case.get("expect_data", False) and resp_json["code"] == 0:
            assert resp_json["method"] == "public/get-candlestick"

    with allure.step("Schema 驗證"):
        if case.get("expect_data", False) and resp_json["code"] == 0:
            validate(instance=resp_json, schema=candlestick_schema)

    if case.get("expect_data", False) and resp_json["code"] == 0:
        with allure.step("驗證數據陣列&內容"):
            data = resp_json["result"]["data"]
            assert isinstance(data, list), "data 不是 list"
            assert len(data) > 0, "data 陣列為空"
            if "count" in case:
                assert len(data) == case["count"], f"count: {case['count']}, 但實際回傳 {len(data)} 筆"
                
                
            for i, kline in enumerate(data):
                # 基本欄位驗證
                for key in ["o", "h", "l", "c", "v", "t"]:
                    assert key in kline, f"[{i}] 缺少欄位: {key}"
                try:
                    # 驗證數值轉換及邏輯
                    o, h, l, c = map(float, [kline["o"], kline["h"], kline["l"], kline["c"]])
                    v = float(kline["v"])
                    assert h >= l, f"[{i}] high({h}) < low({l})" # 驗證高價>=低價
                    assert h >= o and h >= c and h >= l # 驗證高價>=低價、開盤價、收盤價
                    assert l <= o and l <= c and l <= h # 驗證低價<=開盤價、收盤價、高價
                    assert v >= 0, f"[{i}] 交易量<0: {v}" # 驗證交易量>=0
                except Exception as e:
                    assert False, f"[{i}] 數值轉換/邏輯異常: {e}"
            # 驗證時間戳間隔
            if len(data) > 1: # K線數量>1的時候檢查
                tf = case.get("timeframe", "M5")
                interval = TIMEFRAME_TO_INTERVAL.get(tf)
                if interval:  # 非月K線
                    for j in range(1, len(data)):
                        diff = data[j]["t"] - data[j-1]["t"]
                        assert diff == interval, f"K線時間間隔不正確，第{j-1}~{j}根:{diff}，預期:{interval}"
                elif tf == "1M": # 月K另外處理因為日期不固定，所以只驗證時間遞增
                    for j in range(1, len(data)):
                        assert data[j]["t"] > data[j-1]["t"], f"月K線時間戳未遞增: {data[j-1]['t']} → {data[j]['t']}"
    else:
        with allure.step("異常或無數據情境"):
            data = resp_json.get("result", {}).get("data", []) # 避免這兩個不存在報錯
            assert resp_json["code"] != 0 or not data, f"異常場景 data: {data}"
