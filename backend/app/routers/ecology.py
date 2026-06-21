from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ecology_service import ecology_service

router = APIRouter(prefix="/ecology", tags=["生态态势感知"])


@router.get("/indicators")
def get_latest_indicators(zone_name: str = None, db: Session = Depends(get_db)):
    return ecology_service.get_latest_indicators(db, zone_name)


@router.get("/indicators/{zone_name}/history")
def get_historical_data(zone_name: str, days: int = Query(7, ge=1, le=90),
                         db: Session = Depends(get_db)):
    return ecology_service.get_historical_data(db, zone_name, days)


@router.get("/anomalies")
def get_anomalies(limit: int = Query(10), db: Session = Depends(get_db)):
    return ecology_service.get_anomalies(db, limit)


@router.get("/health-trend")
def get_health_trend(days: int = Query(30), db: Session = Depends(get_db)):
    return ecology_service.get_health_trend(db, days)


@router.get("/radar")
def get_radar_data(db: Session = Depends(get_db)):
    return ecology_service.get_radar_data(db)
