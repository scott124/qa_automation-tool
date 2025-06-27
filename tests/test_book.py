import pytest
import json
import allure
from api.book_api import BookWSAPI
from schema.book_schema import book_snapshot_schema
from jsonschema import validate

with open("data/book_testdata.json", encoding="utf-8") as f:
    cases = json.load(f)

@allure.feature("WebSocket API - Book訂閱")
@pytest.mark.ws
@pytest.mark.parametrize("case", cases, ids=[c["desc"] for c in cases])
def test_book_snapshot(case, env):
    api = BookWSAPI(env=env)
    with allure.step(f"訂閱 book.{case['instrument_name']}.{case['depth']}"):
        responses = api.subscribe_book(
            instrument_name=case["instrument_name"],
            depth=case["depth"],
            params=case.get("extra_params"),
            min_msgs=5  # 多收幾筆（可依需求調整）
        )
    # 只驗證有 result 欄位的回應
    target_resp = next((r for r in responses if "result" in r), None)
    assert target_resp is not None, "未收到包含 result 的 WebSocket 回應"
    with allure.step("驗證回應格式與業務碼"):
        validate(instance=target_resp, schema=book_snapshot_schema)
        assert target_resp["code"] == case["expected_code"]
        if target_resp["code"] == 0 and case.get("expect_data"):
            assert "result" in target_resp and "data" in target_resp["result"]
            assert isinstance(target_resp["result"]["data"], list)
        # 不驗證無 result、或錯誤回應格式

