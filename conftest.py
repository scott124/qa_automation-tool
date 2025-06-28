import pytest
import shutil
import os

def pytest_addoption(parser): #新增cmd指令，可切換環境
    parser.addoption(
        "--env", action="store", default="uat", help="環境: uat 或 prod"
    )

@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")

# 再生成allure報告前，先刪除舊的json報告
@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    report_dir = "allure-results"
    if os.path.exists(report_dir):
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