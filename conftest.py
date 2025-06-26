import pytest
import shutil
import os

# 再生成allure報告前，先刪除舊的json報告
@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """在 pytest 執行前，自動清空 allure 報告資料夾內容"""
    report_dir = "allure-report"
    if os.path.exists(report_dir):
        # 只清空內容
        for f in os.listdir(report_dir):
            fpath = os.path.join(report_dir, f)
            if os.path.isfile(fpath):
                os.remove(fpath)
            else:
                shutil.rmtree(fpath)
        print(f"[pytest] 已清空 {report_dir}/ 內容")
    else:
        os.makedirs(report_dir)
        print(f"[pytest] 建立 {report_dir}/ 資料夾")