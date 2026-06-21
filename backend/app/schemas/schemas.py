from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class EcologicalIndicatorOut(BaseModel):
    id: int
    zone_name: str
    zone_type: str
    lat: float
    lng: float
    vegetation_coverage: float
    species_richness: int
    species_diversity_index: float
    water_quality_index: float
    soil_health_index: float
    air_quality_index: float
    carbon_sequestration: float
    ecological_health_score: float
    anomaly_flag: bool
    recorded_at: datetime
    extra_data: Optional[dict] = None

    class Config:
        from_attributes = True


class FireRiskOut(BaseModel):
    id: int
    zone_name: str
    lat: float
    lng: float
    risk_level: str
    risk_score: float
    temperature: float
    humidity: float
    wind_speed: float
    wind_direction: str
    vegetation_type: str
    drought_index: float
    historical_fire_count: int
    predicted_at: datetime
    patrol_routes: Optional[list] = None

    class Config:
        from_attributes = True


class RiskAlertOut(BaseModel):
    id: int
    alert_type: str
    alert_level: str
    title: str
    description: str
    zone_name: str
    lat: float
    lng: float
    probability: float
    estimated_impact: float
    suggested_actions: Optional[list] = None
    response_plan: Optional[str] = None
    is_active: bool
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ResourceScheduleOut(BaseModel):
    id: int
    patrol_team: str
    team_size: int
    zone_name: str
    route_points: Optional[list] = None
    vehicles: Optional[list] = None
    equipment: Optional[list] = None
    schedule_date: datetime
    shift: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class VisitorFlowOut(BaseModel):
    id: int
    zone_name: str
    visitor_count: int
    capacity: int
    congestion_level: float
    recorded_at: datetime

    class Config:
        from_attributes = True


class ParkZoneOut(BaseModel):
    id: int
    name: str
    zone_type: str
    boundary: Optional[list] = None
    area_km2: float
    description: str
    core_protection: bool
    restriction_level: str

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: Optional[str] = None
    sources: Optional[list] = None


class DashboardStats(BaseModel):
    total_zones: int
    avg_health_score: float
    active_alerts: int
    patrol_teams: int
    visitor_count: int
    fire_risk_avg: float
    today_anomalies: int


class ResourceScheduleCreate(BaseModel):
    patrol_team: str = Field(..., description="巡护队伍名称")
    team_size: int = Field(..., ge=1, le=50, description="队伍人数")
    zone_name: str = Field(..., description="负责区域")
    route_points: Optional[list] = Field(default=None, description="巡护路线坐标点")
    vehicles: Optional[list] = Field(default=None, description="配备车辆")
    equipment: Optional[list] = Field(default=None, description="配备装备")
    schedule_date: datetime = Field(default_factory=datetime.now, description="调度日期")
    shift: str = Field(default="morning", description="班次")
    status: str = Field(default="scheduled", description="状态")

    @field_validator("shift")
    @classmethod
    def validate_shift(cls, v: str) -> str:
        if v not in ("morning", "afternoon", "night"):
            raise ValueError("班次必须是 morning/afternoon/night 之一")
        return v


class OptimizeRoutesRequest(BaseModel):
    zone_name: str = Field(..., description="区域名称")
    team_count: int = Field(default=1, ge=1, le=10, description="巡护队伍数量")


class SimulateSpreadRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="火源纬度")
    lng: float = Field(..., ge=-180, le=180, description="火源经度")
    hours: int = Field(default=6, ge=1, le=72, description="模拟时长(小时)")


class FireRiskCalculateRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    temperature: float = Field(..., ge=-50, le=60, description="气温(°C)")
    humidity: float = Field(..., ge=0, le=100, description="湿度(%)")
    wind_speed: float = Field(..., ge=0, le=100, description="风速(m/s)")
    drought_index: float = Field(..., ge=0, le=100, description="干旱指数")
    vegetation_type: str = Field(..., description="植被类型")


class ChatContextRequest(BaseModel):
    message: str = Field(..., description="用户消息")
