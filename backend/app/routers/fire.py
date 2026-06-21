from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.fire_service import fire_service

router = APIRouter(prefix="/fire", tags=["火灾防治管控"])


@router.get("/risks")
def get_current_risks(db: Session = Depends(get_db)):
    return fire_service.get_current_risks(db)


@router.get("/risks/{zone_name}")
def get_zone_risk(zone_name: str, db: Session = Depends(get_db)):
    return fire_service.get_risk_by_zone(db, zone_name)


@router.post("/routes/optimize")
def optimize_patrol_routes(zone_name: str = Body(...), team_count: int = Body(1),
                           db: Session = Depends(get_db)):
    return fire_service.optimize_patrol_routes(db, zone_name, team_count)


@router.post("/spread/simulate")
def simulate_spread(lat: float = Body(...), lng: float = Body(...),
                    hours: int = Body(6)):
    return fire_service.simulate_fire_spread(lat, lng, hours)


@router.post("/risk/calculate")
def calculate_risk(lat: float = Body(...), lng: float = Body(...),
                   temperature: float = Body(...), humidity: float = Body(...),
                   wind_speed: float = Body(...), drought_index: float = Body(...),
                   vegetation_type: str = Body(...)):
    return fire_service.calculate_fire_risk(
        lat, lng, temperature, humidity, wind_speed, drought_index, vegetation_type
    )


@router.get("/correlation")
def get_correlation_data(db: Session = Depends(get_db)):
    return fire_service.get_correlation_data(db)


@router.get("/heatmap")
def get_heatmap_data(db: Session = Depends(get_db)):
    return fire_service.get_heatmap_data(db)
