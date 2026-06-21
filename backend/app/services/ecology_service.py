from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.models import EcologicalIndicator, ParkZone, VisitorFlow


class EcologyService:

    @staticmethod
    def get_latest_indicators(db: Session, zone_name: str = None):
        sub = db.query(
            func.max(EcologicalIndicator.id).label("max_id"),
            EcologicalIndicator.zone_name
        ).group_by(EcologicalIndicator.zone_name)
        if zone_name:
            sub = sub.having(EcologicalIndicator.zone_name == zone_name)
        sub = sub.subquery()
        max_ids = [row.max_id for row in db.query(sub.c.max_id).all()]
        return db.query(EcologicalIndicator).filter(
            EcologicalIndicator.id.in_(max_ids)
        ).all()

    @staticmethod
    def get_historical_data(db: Session, zone_name: str, days: int = 7):
        records = db.query(EcologicalIndicator).filter(
            EcologicalIndicator.zone_name == zone_name
        ).order_by(desc(EcologicalIndicator.recorded_at)).limit(days).all()
        return list(reversed(records))

    @staticmethod
    def get_anomalies(db: Session, limit: int = 10):
        return db.query(EcologicalIndicator).filter(
            EcologicalIndicator.anomaly_flag == True
        ).order_by(desc(EcologicalIndicator.recorded_at)).limit(limit).all()

    @staticmethod
    def get_health_trend(db: Session, days: int = 30):
        records = db.query(EcologicalIndicator).order_by(
            desc(EcologicalIndicator.recorded_at)
        ).limit(days * 8).all()

        zones = {}
        for r in records:
            day = r.recorded_at.strftime("%m-%d")
            if day not in zones:
                zones[day] = []
            zones[day].append(r.ecological_health_score)

        return [{"date": k, "avg_health": round(sum(v) / len(v), 1)} for k, v in sorted(zones.items())]

    @staticmethod
    def get_radar_data(db: Session):
        latest_ids = db.query(func.max(EcologicalIndicator.id)).group_by(
            EcologicalIndicator.zone_name
        ).all()
        latest_ids = [x[0] for x in latest_ids]
        indicators = db.query(EcologicalIndicator).filter(
            EcologicalIndicator.id.in_(latest_ids)
        ).all()

        dimensions = [
            {"name": "植被覆盖", "key": "vegetation_coverage", "max": 100},
            {"name": "水质指数", "key": "water_quality_index", "max": 100},
            {"name": "土壤健康", "key": "soil_health_index", "max": 100},
            {"name": "空气质量", "key": "air_quality_index", "max": 100},
            {"name": "物种多样性", "key": "species_diversity_index", "max": 5},
            {"name": "健康评分", "key": "ecological_health_score", "max": 100},
        ]

        series = []
        for ind in indicators:
            values = []
            for d in dimensions:
                raw = getattr(ind, d["key"], 0) or 0
                values.append(round(raw / d["max"] * 100, 1))
            series.append({
                "name": ind.zone_name,
                "value": values,
                "detail": {
                    "vegetation_coverage": ind.vegetation_coverage,
                    "water_quality_index": ind.water_quality_index,
                    "soil_health_index": ind.soil_health_index,
                    "air_quality_index": ind.air_quality_index,
                    "species_diversity_index": ind.species_diversity_index,
                    "ecological_health_score": ind.ecological_health_score,
                }
            })

        return {
            "indicators": [{"name": d["name"], "max": d["max"]} for d in dimensions],
            "series": series,
        }

    @staticmethod
    def get_zone_summary(db: Session):
        zones = db.query(ParkZone).all()
        latest = db.query(EcologicalIndicator).filter(
            EcologicalIndicator.id.in_(
                db.query(func.max(EcologicalIndicator.id)).group_by(EcologicalIndicator.zone_name)
            )
        ).all()

        result = []
        for z in zones:
            indicator = next((x for x in latest if x.zone_name == z.name), None)
            result.append({
                "name": z.name,
                "type": z.zone_type,
                "area_km2": z.area_km2,
                "lat": z.lat, "lng": z.lng,
                "core_protection": z.core_protection,
                "health_score": indicator.ecological_health_score if indicator else None,
                "anomaly": indicator.anomaly_flag if indicator else False,
                "visitor_capacity": int(z.area_km2 * 1.5),
                "current_visitors": int(z.area_km2 * random_val()),
            })
        return result


def random_val():
    import random
    return random.uniform(0.1, 0.9)


ecology_service = EcologyService()
