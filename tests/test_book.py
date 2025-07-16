import pytest
import json
import allure
from api.book_api import BookWSAPI
from schema.book_schema import book_snapshot_schema
from jsonschema import validate

with open("data/book_testdata.json", encoding="utf-8") as f:
    cases = json.load(f)

@allure.feature("WebSocket API - Book")
@pytest.mark.ws
@pytest.mark.parametrize("case", cases, ids=[c["desc"] for c in cases])
def test_book_snapshot(case, env):
    api = BookWSAPI(env=env)
    with allure.step(f"訂單 {env} 環境 book.{case['instrument_name']}.{case['depth']} 頻道"):
        responses = api.subscribe_book(
            instrument_name=case["instrument_name"],
            depth=case["depth"],
            params=case.get("extra_params"),
            min_msgs=5
        )

    with allure.step("篩選回應：含 result 或 subscribe/error"):
        # 嘗試撈出含 result 的訊息
        result_resp = next((r for r in responses if "result" in r), None)
        
        # 或出錯誤訊息，增加code!=0且沒有result (怕撈出heartbeat
        error_resp = next((r for r in responses if r.get("code", 0) != 0 and "result" not in r),None)
        
    # ==== 正常/有資料情境 ====
    if case.get("expect_data", False) and result_resp and result_resp.get("code") == 0:
        with allure.step("驗證 snapshot/資料內容"):
            validate(instance=result_resp, schema=book_snapshot_schema)
            assert result_resp["code"] == case["expected_code"], f"code: {result_resp['code']} (期望: {case['expected_code']})"
            result = result_resp["result"]
            data = result["data"]
            assert isinstance(data, list), "data 欄位不是 list"
            assert len(data) > 0, "data 陣列為空"

            # ====== instrument動態驗證，單一、多交易對情況下皆適用 ======
            if "extra_params" in case and "channels" in case["extra_params"]:
                expect_instruments = [ch.split(".")[1] for ch in case["extra_params"]["channels"]] #[1]為交易對名稱
                assert result["instrument_name"] in expect_instruments, \
                    f"交易對不符: {result['instrument_name']} 不在預期: {expect_instruments}"
            else:
                assert result["instrument_name"] == case["instrument_name"], \
                    f"交易對不符: {result['instrument_name']} != {case['instrument_name']}"

            with allure.step("驗證 channel、instrument_name、depth 都等於預期"):
                assert result["channel"].startswith("book"), f"channel 欄位錯誤: {result['channel']}"
                assert int(result["depth"]) == int(case["depth"]), f"深度不符: {result['depth']} != {case['depth']}"

            for i, entry in enumerate(data):
                with allure.step(f"驗證第 {i} 筆 bids/asks 結構與數值"):
                    assert "bids" in entry and "asks" in entry, "缺少 bids 或 asks 欄位"
                    assert isinstance(entry["bids"], list), "bids 不是 list"
                    assert isinstance(entry["asks"], list), "asks 不是 list"
                    for bid in entry["bids"]:
                        assert isinstance(bid, list) and len(bid) == 3, f"bids[{bid}] 結構錯誤"
                        price, size, order_count = bid
                        float(price)
                        float(size)
                        int(order_count)
                    for ask in entry["asks"]:
                        assert isinstance(ask, list) and len(ask) == 3, f"asks[{ask}] 結構錯誤"
                        price, size, order_count = ask
                        float(price)
                        float(size)
                        int(order_count)

                with allure.step(f"驗證買單<=賣單"):
                    if entry["bids"] and entry["asks"]:
                        best_bid = float(entry["bids"][0][0])
                        best_ask = float(entry["asks"][0][0])
                        assert best_bid <= best_ask, f"買一({best_bid}) 應小於等於賣一({best_ask})"

                with allure.step(f"驗證 bids/asks 排序"):
                    if len(entry["bids"]) > 1:
                        prices = [float(b[0]) for b in entry["bids"]]
                        assert prices == sorted(prices, reverse=True), f"bids 價格排序錯誤: {prices}"
                    if len(entry["asks"]) > 1:
                        prices = [float(a[0]) for a in entry["asks"]]
                        assert prices == sorted(prices), f"asks 價格排序錯誤: {prices}"

            with allure.step("驗證時間戳為 int 且應持續遞增"):
                times = [entry["t"] for entry in data]
                assert all(isinstance(t, int) for t in times), "t 不是 int"
                if len(times) > 1:
                    assert all(times[i] <= times[i+1] for i in range(len(times)-1)), f"t 非遞增: {times}"

    # ==== 錯誤情境(反向測試) ====
    else:
        with allure.step("異常或無數據情境"):
            assert error_resp is not None, "未收到訂單異常回應"
            assert error_resp["code"] == case["expected_code"], f"code: {error_resp['code']} (期望: {case['expected_code']})"
            if "expected_message" in case:
                assert error_resp.get("message", "") == case["expected_message"], f"message: {error_resp.get('message', '')} (期望: {case['expected_message']})"


@allure.feature("WebSocket API - method not found")
@pytest.mark.ws
def test_ws_invalid_method(env):
    api = BookWSAPI(env=env)
    api.ws_client.connect()
    payload = {
        "id": 1,
        "method": "HI!!!",  
        "params": {
            "channels": ["book.BTCUSD-PERP.10"]
        }
    }
    api.ws_client.send(payload)
    responses = api.ws_client.get_responses(min_count=2)
    api.ws_client.close()
    # 轉成dict，為了要用.get() 
    responses = [json.loads(r) if isinstance(r, str) else r for r in responses]
    error_resp = next((r for r in responses if r.get("code", 0) != 0), None)
    assert error_resp is not None, "未收到異常回應"
    assert error_resp["code"] == 40003    
    assert error_resp.get("message", "") == "No such method"
