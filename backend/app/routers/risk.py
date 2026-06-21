from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.risk_service import risk_service

router = APIRouter(prefix="/risk", tags=["风险预警与应急响应"])


@router.get("/alerts")
def get_active_alerts(db: Session = Depends(get_db)):
    return risk_service.get_active_alerts(db)


@router.get("/alerts/history")
def get_alert_history(limit: int = Query(20), db: Session = Depends(get_db)):
    return risk_service.get_alert_history(db, limit)


@router.get("/alerts/level/{level}")
def get_alerts_by_level(level: str, db: Session = Depends(get_db)):
    return risk_service.get_alerts_by_level(db, level)


@router.post("/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    return risk_service.resolve_alert(db, alert_id)


@router.get("/alerts/plan")
def generate_response_plan(alert_type: str, alert_level: str, zone_name: str):
    return risk_service.generate_response_plan(alert_type, alert_level, zone_name)


@router.get("/stats")
def get_alert_stats(db: Session = Depends(get_db)):
    return risk_service.get_alert_stats(db)


@router.get("/timeline")
def get_alert_timeline(limit: int = Query(30), db: Session = Depends(get_db)):
    return risk_service.get_timeline_data(db, limit)
