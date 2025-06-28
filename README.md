# crypto.com QA 測試專案

## 架構圖

```
crypto.com_qa/
├── api/                   # API、WebSocket 封裝
│   ├── base_api.py
│   ├── candlestick_api.py
│   ├── base_ws.py
│   └── book_api.py
├── data/                  # 測試資料
│   ├── candlestick_testdata.json
│   └── book_testdata.json
├── schema/                # jsonschema 驗證
│   ├── candlestick_schema.py
│   └── book_schema.py
├── utils/                 # 工具
│   └── timeframe.py
├── tests/                 # 測試案例
│   ├── test_candlestick.py
│   └── test_book.py
├── config.toml            # 多環境/連線設定
├── requirements.txt       # Python 依賴包清單
├── .gitignore
├── pytest.ini             # pytest mark 設定
└── README.md
```

## 環境安裝

在專案目錄下執行：

```bash
pip install -r requirements.txt
```

### 安裝 Allure 報告工具

需另外安裝 Allure，建議使用 scoop 安裝：

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
scoop install allure
```

## 常用指令說明

* `-m`：只執行被標記的測試案例。
* `-s`：顯示所有 `print` 語句及其他輸出。
* `-v`：顯示更詳細訊息，包括完整測試名稱。
* `--tb=short`：失敗時僅顯示精簡追蹤訊息。
* `--lf`：僅執行上次失敗的測試案例。
* `--env`：指定測試運行環境，未填寫預設環境為UAV。
* `--alluredir`：指定 Allure 報告輸出目錄。

## 測試執行

切換到專案根目錄 `crypto.com_qa` 下執行以下指令。

### 執行所有測試（含 API 與 WebSocket）：

```bash
pytest
```

### 執行測試並產生 Allure 報告：

```bash
pytest --alluredir=allure-results
```

### 開啟 Allure 報告

```bash
allure serve allure-results
```

### 指定環境與測試類型（API/WebSocket）

例如執行 prod 環境下的 API 測試並產生報告：

```bash
pytest --env prod -m api --alluredir=allure-results
```
