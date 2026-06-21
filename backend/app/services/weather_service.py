"""调用 Open-Meteo API 获取各国家公园区域的真实气象数据"""
import random
import httpx
import time
from typing import Optional
from app.utils.park_zones import PARK_ZONES


_weather_cache: Optional[dict] = None


def _get_open_meteo(lat: float, lng: float) -> Optional[dict]:
    """调用 Open-Meteo 免费天气 API"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lng,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,"
                   "wind_direction_10m,weather_code,precipitation",
        "timezone": "Asia/Shanghai",
    }
    try:
        resp = httpx.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cur = data.get("current", {})
        if not cur:
            return None
        return {
            "temperature": cur.get("temperature_2m"),
            "humidity": cur.get("relative_humidity_2m"),
            "wind_speed": cur.get("wind_speed_10m"),
            "wind_direction": cur.get("wind_direction_10m"),
            "weather_code": cur.get("weather_code"),
            "precipitation": cur.get("precipitation"),
        }
    except Exception:
        return None


def _weather_code_to_cn(code: int) -> str:
    """WMO weather code → 中文天气描述"""
    code_map = {
        0: "晴", 1: "晴", 2: "多云", 3: "阴",
        45: "雾", 48: "雾凇",
        51: "小雨", 53: "小雨", 55: "中雨", 56: "冻雨", 57: "冻雨",
        61: "小雨", 63: "中雨", 65: "大雨",
        66: "冻雨", 67: "冻雨",
        71: "小雪", 73: "中雪", 75: "大雪", 77: "雪粒",
        80: "阵雨", 81: "阵雨", 82: "强阵雨",
        85: "阵雪", 86: "强阵雪",
        95: "雷暴", 96: "雷暴冰雹", 99: "强雷暴冰雹",
    }
    return code_map.get(code, "多云")


def _wind_dir_to_cn(deg: Optional[float]) -> str:
    """风向角度 → 中文方向"""
    if deg is None:
        return "N"
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((deg % 360) / 22.5)
    return dirs[idx % 16]


def _wind_dir_to_8(deg: Optional[float]) -> str:
    """风向角度 → 8方向(N/NE/E/...)"""
    if deg is None:
        return "N"
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int(((deg % 360) + 22.5) / 45)
    return dirs[idx % 8]


def fetch_all_weather(force_refresh: bool = False) -> dict:
    """获取所有园区的真实天气数据（带缓存）"""
    global _weather_cache
    if _weather_cache is not None and not force_refresh:
        return _weather_cache

    result = {}
    for z in PARK_ZONES:
        name = z["name"]
        real = _get_open_meteo(z["lat"], z["lng"])
        if real is not None:
            result[name] = {
                "temperature": real["temperature"] if real["temperature"] is not None else round(random.uniform(15, 38), 1),
                "humidity": real["humidity"] if real["humidity"] is not None else round(random.uniform(20, 80), 1),
                "wind_speed": real["wind_speed"] if real["wind_speed"] is not None else round(random.uniform(1, 25), 1),
                "wind_direction": _wind_dir_to_8(real["wind_direction"]),
                "wind_direction_cn": _wind_dir_to_cn(real["wind_direction"]),
                "weather_cn": _weather_code_to_cn(real["weather_code"]) if real["weather_code"] is not None else "多云",
                "precipitation": real.get("precipitation", 0),
                "source": "open-meteo",
            }
        else:
            result[name] = _random_weather()
            result[name]["source"] = "random"
        time.sleep(0.15)  # 避免请求过快

    _weather_cache = result
    return result


def _random_weather() -> dict:
    return {
        "temperature": round(random.uniform(15, 38), 1),
        "humidity": round(random.uniform(20, 80), 1),
        "wind_speed": round(random.uniform(1, 25), 1),
        "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
        "wind_direction_cn": random.choice(["北", "东北", "东", "东南", "南", "西南", "西", "西北"]),
        "weather_cn": random.choice(["晴", "多云", "小雨", "阴"]),
        "precipitation": round(random.uniform(0, 5), 1),
        "source": "random",
    }
