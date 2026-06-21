import random
import math
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.models import FireRiskAssessment, ParkZone


class FireService:

    @staticmethod
    def get_current_risks(db: Session):
        return db.query(FireRiskAssessment).order_by(
            FireRiskAssessment.predicted_at.desc()
        ).limit(8).all()

    @staticmethod
    def get_risk_by_zone(db: Session, zone_name: str = None):
        q = db.query(FireRiskAssessment)
        if zone_name:
            q = q.filter(FireRiskAssessment.zone_name == zone_name)
        return q.order_by(FireRiskAssessment.predicted_at.desc()).first()

    @staticmethod
    def optimize_patrol_routes(db: Session, zone_name: str, team_count: int = 1):
        zone = db.query(ParkZone).filter(ParkZone.name == zone_name).first()
        risk = db.query(FireRiskAssessment).filter(
            FireRiskAssessment.zone_name == zone_name
        ).order_by(FireRiskAssessment.predicted_at.desc()).first()

        if not zone:
            return {"error": "区域不存在"}

        center_lat, center_lng = zone.lat, zone.lng

        veg_type = risk.vegetation_type if risk else zone.zone_type or "森林"
        risk_level = risk.risk_level if risk else "medium"

        area = (zone.area_km2 or 2000)
        base_radius = max(0.05, min(1.2, math.sqrt(area) / 200))
        patrol_radius = base_radius * (1.5 if risk_level in ("high", "extreme") else 1.2)
        point_count = 8 if risk_level in ("high", "extreme") else 5

        terrain_offset = {
            "森林": (0.008, 0.006), "草原": (0.015, 0.01), "阔叶林": (0.008, 0.007),
            "针叶林": (0.006, 0.005), "灌丛": (0.01, 0.008), "高山草甸": (0.012, 0.01),
            "湿地": (0.01, 0.012), "高山": (0.01, 0.008), "热带雨林": (0.005, 0.004),
        }
        offset_lat, offset_lng = terrain_offset.get(veg_type, (0.01, 0.01))

        boundary = zone.boundary if isinstance(zone.boundary, list) and len(zone.boundary) >= 3 else None

        routes = []
        sector_angle = 360.0 / team_count

        for t in range(team_count):
            start_deg = sector_angle * t + random.uniform(-10, 10)
            points = []

            if boundary and t < len(boundary):
                bps = boundary
            else:
                bps = None

            for i in range(point_count):
                if bps and i < len(bps):
                    bp = bps[i % len(bps)]
                    bl, bn = (bp[0], bp[1]) if isinstance(bp, (list, tuple)) and len(bp) == 2 else (bp.get("lat", center_lat), bp.get("lng", center_lng))
                    lat = round(bl + random.uniform(-offset_lat, offset_lat), 4)
                    lng = round(bn + random.uniform(-offset_lng, offset_lng), 4)
                else:
                    progress = i / max(point_count - 1, 1)
                    arc_deg = start_deg + sector_angle * progress * random.uniform(0.8, 1.2)
                    r = patrol_radius * (0.6 + 0.4 * abs(math.sin(progress * math.pi)))
                    lat = round(center_lat + r * math.cos(math.radians(arc_deg)), 4)
                    lng = round(center_lng + r * math.sin(math.radians(arc_deg)), 4)

                points.append({"lat": lat, "lng": lng})

            routes.append({
                "team": f"巡护队-{t+1}",
                "route": points,
                "estimated_hours": round(random.uniform(1.5, 3.5) * (1.2 if risk_level in ("high", "extreme") else 1.0), 1),
                "priority_areas": len(points),
            })

        return {"zone": zone_name, "routes": routes}

    @staticmethod
    def simulate_fire_spread(lat: float, lng: float, hours: int = 6):
        spread = []
        for h in range(1, hours + 1):
            r = h * random.uniform(0.01, 0.03)
            spread.append({
                "hour": h,
                "radius_km": round(r * 111, 2),
                "affected_area_km2": round(math.pi * (r * 111) ** 2, 2),
                "confidence": round(max(0.3, 1.0 - h * 0.08), 2),
            })
        return {
            "origin": {"lat": lat, "lng": lng},
            "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
            "wind_speed": random.uniform(1, 20),
            "prediction": spread,
        }

    @staticmethod
    def get_correlation_data(db: Session):
        risks = db.query(FireRiskAssessment).all()
        seen = set()
        result = []
        for r in risks:
            if r.zone_name not in seen:
                seen.add(r.zone_name)
                result.append({
                    "zone_name": r.zone_name,
                    "temperature": r.temperature,
                    "humidity": r.humidity,
                    "wind_speed": r.wind_speed,
                    "drought_index": r.drought_index,
                    "risk_score": r.risk_score,
                    "risk_level": r.risk_level,
                })
        return result

    @staticmethod
    def get_heatmap_data(db: Session):
        import random as _rnd
        risks = db.query(FireRiskAssessment).all()
        heatmap_points = []
        for r in risks:
            for _ in range(8):
                heatmap_points.append({
                    "lat": round(r.lat + _rnd.uniform(-0.5, 0.5), 4),
                    "lng": round(r.lng + _rnd.uniform(-0.5, 0.5), 4),
                    "value": round(r.risk_score * _rnd.uniform(0.6, 1.4), 1),
                    "zone_name": r.zone_name,
                })
        return heatmap_points

    @staticmethod
    def calculate_fire_risk(lat: float, lng: float, temp: float, humidity: float,
                            wind: float, drought: float, veg_type: str):
        veg_weights = {"针叶林": 1.2, "阔叶林": 0.9, "灌丛": 1.1, "草原": 1.3, "高山草甸": 0.7}
        veg_w = veg_weights.get(veg_type, 1.0)
        score = (temp * 1.5 + (100 - humidity) * 0.8 + wind * 1.2 + drought * 0.5) / 4 * veg_w
        score = min(100, max(0, score + random.uniform(-10, 10)))

        level = "low"
        if score > 70:
            level = "extreme"
        elif score > 50:
            level = "high"
        elif score > 30:
            level = "medium"

        return {
            "risk_score": round(score, 1),
            "risk_level": level,
            "factors": {
                "temperature_contribution": round(temp * 1.5 / 4, 1),
                "humidity_contribution": round((100 - humidity) * 0.8 / 4, 1),
                "wind_contribution": round(wind * 1.2 / 4, 1),
                "drought_contribution": round(drought * 0.5 / 4, 1),
                "vegetation_multiplier": veg_w,
            }
        }


fire_service = FireService()
