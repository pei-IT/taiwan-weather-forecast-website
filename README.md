# 台灣天氣預報網站

使用中央氣象署（CWA）開放資料平台 API 建立的天氣預報網站。

## 功能

- 📋 全台 22 縣市 36 小時天氣預報
- � 未來一週天氣預報
- �🔍 依縣市篩選查詢
- � 即時氣象觀測站資料
- �📱 響應式設計，支援手機與桌面瀏覽
- 🎨 美觀的天氣圖示與卡片式介面
- 🌐 支援 GitHub Pages 靜態部署（無需後端）

## 技術架構

- **後端**：Python + FastAPI + Uvicorn
- **前端**：HTML5 + CSS3 + Vanilla JavaScript
- **HTTP 客戶端**：httpx（非同步請求）
- **資料來源**：中央氣象署開放資料平台 API
- **測試**：Playwright（E2E）
- **部署**：Docker / GitHub Pages

## 使用的 API 資料集

| 資料集代碼 | 說明 |
|-----------|------|
| F-C0032-001 | 一般天氣預報 - 今明 36 小時天氣預報 |
| F-D0047-091 | 一般天氣預報 - 未來一週天氣預報 |
| O-A0003-001 | 自動氣象站觀測資料 |

## 專案結構

```
├── app.py             # FastAPI 後端伺服器
├── requirements.txt   # Python 依賴套件
├── public/
│   ├── index.html     # 前端頁面
│   ├── styles.css     # 樣式表
│   └── app.js         # 前端 JavaScript
├── tests/
│   └── example.spec.js  # Playwright E2E 測試
├── docker-compose.yml # Docker 部署設定
├── package.json       # Playwright 測試設定
├── .env.example       # 環境變數範例
├── .env               # 環境變數（不納入版控）
└── .gitignore
```

## 快速開始

### 1. 取得 API 授權碼

前往 [中央氣象署開放資料平台](https://opendata.cwa.gov.tw/) 註冊帳號並取得授權碼。

### 2. 設定環境變數

```bash
cp .env.example .env
```

編輯 `.env`，填入你的授權碼：

```
CWA_API_KEY=你的授權碼
PORT=3001
```

### 3. 安裝依賴並啟動

```bash
pip install -r requirements.txt
python app.py
```

伺服器啟動後開啟瀏覽器前往 http://localhost:3001

API 文件（Swagger UI）：http://localhost:3001/docs

### 4. Docker 部署

```bash
docker compose up -d
```

## API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/forecast/36hr` | 36 小時天氣預報（可選 `?locationName=臺北市`） |
| GET | `/api/forecast/week` | 一週天氣預報（可選 `?locationName=臺北市`） |
| GET | `/api/observation` | 即時氣象觀測站資料 |
| GET | `/api/debug/week` | 除錯用：查看 API 原始回傳結構 |

## GitHub Pages 部署

前端支援直接部署至 GitHub Pages，不需要後端伺服器。`public/app.js` 會自動偵測環境，在 GitHub Pages 上直接呼叫氣象署 API。

## 授權

資料來源：[交通部中央氣象署開放資料平台](https://opendata.cwa.gov.tw/)
