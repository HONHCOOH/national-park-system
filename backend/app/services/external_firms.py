import random
import httpx
from typing import Optional


def _get_zone_bbox(zone: dict):
    boundary = zone.get("boundary", [])
    if boundary and len(boundary) >= 2:
        lats = [p[0] if isinstance(p, (list, tuple)) else p.get("lat", 0) for p in boundary]
        lngs = [p[1] if isinstance(p, (list, tuple)) else p.get("lng", 0) for p in boundary]
        return min(lat for lat in lats), min(lng for lng in lngs), max(lat for lat in lats), max(lng for lng in lngs)
    lat, lng = zone["lat"], zone["lng"]
    margin = 0.3
    return lat - margin, lng - margin, lat + margin, lng + margin


def _fetch_firms_hotspots(api_key: str, south: float, west: float, north: float, east: float,
                          days: int = 7) -> Optional[list]:
    if not api_key:
        return None

    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/json/{api_key}/VIIRS_SNPP_NRT/{west},{south},{east},{north}/{days}"
    try:
        resp = httpx.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        return None
    except Exception:
        return None


def fetch_all_fire_counts(api_key: str = "", days: int = 30) -> dict:
    from app.utils.park_zones import PARK_ZONES

    result = {}
    for z in PARK_ZONES:
        name = z["name"]
        south, west, north, east = _get_zone_bbox(z)

        hotspots = _fetch_firms_hotspots(api_key, south, west, north, east, days)

        if hotspots is not None:
            count = len(hotspots)
            result[name] = {
                "historical_fire_count": count,
                "hotspots": hotspots[:20],
                "source": "nasa-firms",
            }
        else:
            result[name] = {
                "historical_fire_count": None,
                "hotspots": [],
                "source": "unavailable" if not api_key else "api-error",
            }

    return result


def get_historical_fire_count(zone_name: str, api_key: str = "", days: int = 30) -> Optional[int]:
    fires = fetch_all_fire_counts(api_key, days)
    data = fires.get(zone_name)
    if data and data["historical_fire_count"] is not None:
        return data["historical_fire_count"]
    return None
