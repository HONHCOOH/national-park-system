from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.resource_service import resource_service

router = APIRouter(prefix="/resource", tags=["管理协同与资源调度"])


@router.get("/schedules")
def get_schedules(limit: int = Query(20), db: Session = Depends(get_db)):
    return resource_service.get_schedules(db, limit)


@router.get("/schedules/{zone_name}")
def get_zone_schedules(zone_name: str, db: Session = Depends(get_db)):
    return resource_service.get_schedules_by_zone(db, zone_name)


@router.post("/schedules")
def create_schedule(data: dict = Body(...), db: Session = Depends(get_db)):
    return resource_service.create_schedule(db, data)


@router.get("/visitors")
def get_visitor_stats(db: Session = Depends(get_db)):
    return resource_service.get_visitor_stats(db)


@router.get("/allocation/optimize")
def optimize_allocation(db: Session = Depends(get_db)):
    return resource_service.optimize_allocation(db)


@router.get("/patrol-logs")
def get_patrol_logs(limit: int = Query(10), db: Session = Depends(get_db)):
    return resource_service.get_patrol_logs(db, limit)


@router.get("/flow")
def get_resource_flow(db: Session = Depends(get_db)):
    return resource_service.get_resource_flow(db)
