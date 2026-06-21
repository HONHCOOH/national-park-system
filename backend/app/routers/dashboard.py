from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ecology_service import ecology_service
from app.services.fire_service import fire_service
from app.services.risk_service import risk_service
from app.services.resource_service import resource_service
from app.models.models import ParkZone

router = APIRouter(tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    from app.models.models import EcologicalIndicator, RiskAlert, ResourceSchedule
    from sqlalchemy import func

    zones = db.query(ParkZone).count()
    anomalies = db.query(EcologicalIndicator).filter(
        EcologicalIndicator.anomaly_flag == True,
    ).count()
    active_alerts = db.query(RiskAlert).filter(
        RiskAlert.is_active == True,
    ).count()
    patrol_teams = db.query(ResourceSchedule).filter(
        ResourceSchedule.status.in_(["scheduled", "in_progress"])
    ).count()

    avg_health = db.query(func.avg(EcologicalIndicator.ecological_health_score)).scalar() or 0

    return {
        "total_zones": zones,
        "avg_health_score": round(avg_health, 1),
        "active_alerts": active_alerts,
        "patrol_teams": patrol_teams,
        "today_anomalies": anomalies,
        "fire_risk_avg": 35.2,
        "visitor_count": 1280,
        "eco_health_trend": ecology_service.get_health_trend(db, 7),
        "alert_distribution": risk_service.get_alert_stats(db),
    }


@router.get("/zones")
def get_all_zones(db: Session = Depends(get_db)):
    zones = db.query(ParkZone).all()
    from app.models.models import EcologicalIndicator
    from sqlalchemy import func

    latest_ids = db.query(func.max(EcologicalIndicator.id)).group_by(
        EcologicalIndicator.zone_name
    ).all()
    latest_ids = [x[0] for x in latest_ids]
    latest_indicators = db.query(EcologicalIndicator).filter(
        EcologicalIndicator.id.in_(latest_ids)
    ).all()
    indicator_map = {i.zone_name: i for i in latest_indicators}

    result = []
    for z in zones:
        ind = indicator_map.get(z.name)
        result.append({
            "id": z.id,
            "name": z.name,
            "zone_type": z.zone_type,
            "area_km2": z.area_km2,
            "lat": z.lat, "lng": z.lng,
            "core_protection": z.core_protection,
            "restriction_level": z.restriction_level,
            "description": z.description,
            "boundary": z.boundary,
            "health_score": ind.ecological_health_score if ind else None,
            "anomaly": ind.anomaly_flag if ind else False,
        })
    return result
