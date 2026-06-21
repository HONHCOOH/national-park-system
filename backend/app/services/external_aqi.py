import random
import httpx
import time
from typing import Optional


_aqi_cache: Optional[dict] = None


def _get_open_meteo_aqi(lat: float, lng: float) -> Optional[dict]:
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": lng,
        "current": "european_aqi,pm2_5,pm10",
    }
    try:
        resp = httpx.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cur = data.get("current", {})
        if not cur:
            return None
        return {
            "european_aqi": cur.get("european_aqi"),
            "pm2_5": cur.get("pm2_5"),
            "pm10": cur.get("pm10"),
        }
    except Exception:
        return None


def _european_aqi_to_index(eaqi: Optional[float]) -> Optional[float]:
    if eaqi is None:
        return None
    return round(max(0, min(100, 100 - eaqi * 100 / 300)), 1)


def fetch_all_aqi(force_refresh: bool = False) -> dict:
    global _aqi_cache
    from app.utils.park_zones import PARK_ZONES

    if _aqi_cache is not None and not force_refresh:
        return _aqi_cache

    result = {}
    for z in PARK_ZONES:
        name = z["name"]
        real = _get_open_meteo_aqi(z["lat"], z["lng"])
        if real is not None and real.get("european_aqi") is not None:
            result[name] = {
                "air_quality_index": _european_aqi_to_index(real["european_aqi"]),
                "pm2_5": real.get("pm2_5"),
                "pm10": real.get("pm10"),
                "european_aqi": real["european_aqi"],
                "source": "open-meteo-aqi",
            }
        else:
            result[name] = {
                "air_quality_index": None,
                "pm2_5": None,
                "pm10": None,
                "european_aqi": None,
                "source": "unavailable",
            }
        time.sleep(0.15)

    _aqi_cache = result
    return result


def get_air_quality_index(lat: float, lng: float) -> Optional[float]:
    """Single-point AQI query, with cache fallback to bulk fetch"""
    global _aqi_cache
    from app.utils.park_zones import PARK_ZONES

    bulk = fetch_all_aqi()
    from math import radians, cos, sin, asin, sqrt

    def haversine(lat1, lng1, lat2, lng2):
        dlat = radians(lat2 - lat1)
        dlng = radians(lng2 - lng1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2) ** 2
        return 2 * asin(sqrt(a)) * 6371

    best = None
    best_dist = float("inf")
    for z in PARK_ZONES:
        d = haversine(lat, lng, z["lat"], z["lng"])
        if d < best_dist:
            best_dist = d
            z_name = z["name"]
            best = bulk.get(z_name)

    if best and best["air_quality_index"] is not None:
        return best["air_quality_index"]
    return None
