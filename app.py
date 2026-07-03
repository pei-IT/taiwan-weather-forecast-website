"""
台灣天氣預報網站 - FastAPI 後端
資料來源：中央氣象署開放資料平台

啟動方式（不需要虛擬環境）：
  pip install fastapi uvicorn httpx python-dotenv
  python app.py
"""

import os
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# 載入 .env 環境變數
load_dotenv()

CWA_API_KEY = os.getenv("CWA_API_KEY", "")
PORT = int(os.getenv("PORT", "3001"))

# 中央氣象署 API 基礎網址
CWA_BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore"

app = FastAPI(
    title="台灣天氣預報 API",
    description="使用中央氣象署開放資料的天氣預報服務",
    version="1.0.0",
)

# CORS 中介軟體
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def fetch_cwa(dataset_id: str, params: Optional[dict] = None) -> dict:
    """
    共用的 CWA API 請求函式
    使用 Header 傳遞授權碼，避免被 WAF 擋掉
    """
    if params is None:
        params = {}

    url = f"{CWA_BASE_URL}/{dataset_id}"
    headers = {
        "Authorization": CWA_API_KEY,
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
        response = await client.get(url, headers=headers, params=params)

    if response.status_code != 200:
        error_text = response.text[:200]
        return JSONResponse(
            status_code=response.status_code,
            content={"success": False, "message": f"CWA API 回應錯誤 ({response.status_code}): {error_text}"},
        )

    return response.json()


# ============================================================
# API 端點
# ============================================================


@app.get("/api/forecast/36hr")
async def get_forecast_36hr(locationName: Optional[str] = Query(None)):
    """
    取得一般天氣預報 - 今明36小時天氣預報
    資料集代碼：F-C0032-001
    """
    try:
        params = {}
        if locationName:
            params["locationName"] = locationName

        data = await fetch_cwa("F-C0032-001", params)

        # 如果 fetch_cwa 回傳的是 JSONResponse（錯誤），直接回傳
        if isinstance(data, JSONResponse):
            return data

        if data.get("success") in ("true", True):
            return {"success": True, "data": data["records"]["location"]}
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "無法取得天氣資料"},
            )
    except Exception as e:
        print(f"取得36小時預報失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)},
        )


@app.get("/api/forecast/week")
async def get_forecast_week(locationName: Optional[str] = Query(None)):
    """
    取得一般天氣預報 - 未來 1 週天氣預報
    資料集代碼：F-D0047-091
    """
    try:
        params = {}
        if locationName:
            # F-D0047-091 API 參數需使用大寫 LocationName
            params["LocationName"] = locationName

        data = await fetch_cwa("F-D0047-091", params)

        if isinstance(data, JSONResponse):
            return data

        if data.get("success") in ("true", True):
            records = data["records"]

            # 適應 API 回傳的大寫欄位名稱
            locations = None
            locations_arr = records.get("Locations") or records.get("locations")

            if locations_arr and isinstance(locations_arr, list) and len(locations_arr) > 0:
                locations = locations_arr[0].get("Location") or locations_arr[0].get("location")

            if not locations:
                locations = records.get("Location") or records.get("location")

            # 若 API 未正確過濾，在後端手動過濾指定縣市
            if locations and len(locations) > 1 and locationName:
                filtered = [
                    loc for loc in locations
                    if (loc.get("LocationName") or loc.get("locationName")) == locationName
                ]
                if filtered:
                    locations = filtered

            if locations and len(locations) > 0:
                return {"success": True, "data": locations}
            else:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "message": "查無天氣預報資料"},
                )
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "無法取得一週天氣資料，請確認 API 授權碼是否正確"},
            )
    except Exception as e:
        print(f"取得一週預報失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)},
        )


@app.get("/api/observation")
async def get_observation():
    """
    取得目前天氣觀測資料
    資料集代碼：O-A0003-001 (自動氣象站觀測資料)
    """
    try:
        data = await fetch_cwa("O-A0003-001")

        if isinstance(data, JSONResponse):
            return data

        if data.get("success") in ("true", True):
            return {"success": True, "data": data["records"]["Station"]}
        else:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "無法取得觀測資料"},
            )
    except Exception as e:
        print(f"取得觀測資料失敗: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)},
        )


@app.get("/api/debug/week")
async def debug_week(locationName: Optional[str] = Query(None)):
    """
    除錯用：直接查看 CWA API 原始回傳結構
    """
    try:
        params = {}
        if locationName:
            params["LocationName"] = locationName
        else:
            params["LocationName"] = "臺北市"

        print(f"除錯請求 F-D0047-091, params: {params}")
        data = await fetch_cwa("F-D0047-091", params)

        if isinstance(data, JSONResponse):
            return data

        records = data.get("records", {})
        locations_arr = records.get("Locations") or records.get("locations") or []
        first_group = locations_arr[0] if locations_arr else None
        location_list = (
            (first_group.get("Location") or first_group.get("location"))
            if first_group else None
        )
        first_location = location_list[0] if location_list else None
        weather_elements = (
            (first_location.get("WeatherElement") or first_location.get("weatherElement"))
            if first_location else None
        )
        first_element = weather_elements[0] if weather_elements else None

        return {
            "apiSuccess": data.get("success"),
            "recordKeys": list(records.keys()) if records else None,
            "firstGroupKeys": list(first_group.keys()) if first_group else None,
            "locationCount": len(location_list) if location_list else 0,
            "firstLocationName": (
                (first_location.get("LocationName") or first_location.get("locationName"))
                if first_location else None
            ),
            "weatherElementCount": len(weather_elements) if weather_elements else 0,
            "weatherElementNames": (
                [e.get("ElementName") or e.get("elementName") for e in weather_elements]
                if weather_elements else []
            ),
            "firstElementSample": (
                {
                    "name": first_element.get("ElementName") or first_element.get("elementName"),
                    "keys": list(first_element.keys()),
                    "timeCount": len(first_element.get("Time") or first_element.get("time") or []),
                    "firstTime": (first_element.get("Time") or first_element.get("time") or [None])[0],
                }
                if first_element else None
            ),
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "hint": "請確認 API Key 是否有效"},
        )


# ============================================================
# 靜態檔案（前端）- 必須放在 API 路由之後
# ============================================================

# 掛載 public 資料夾作為靜態檔案
app.mount("/", StaticFiles(directory="public", html=True), name="static")


# ============================================================
# 啟動伺服器
# ============================================================

if __name__ == "__main__":
    import uvicorn

    if not CWA_API_KEY or CWA_API_KEY == "your_api_key_here":
        print("⚠️  請在 .env 檔案中設定 CWA_API_KEY")
        print("   前往 https://opendata.cwa.gov.tw/ 註冊取得授權碼")

    print(f"🌤️ 天氣預報伺服器已啟動: http://localhost:{PORT}")
    print(f"📄 API 文件: http://localhost:{PORT}/docs")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
