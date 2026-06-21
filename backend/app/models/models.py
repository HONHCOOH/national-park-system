import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class EcologicalIndicator(Base):
    __tablename__ = "ecological_indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_name = Column(String(100), comment="监测区域名称")
    zone_type = Column(String(50), comment="区域类型: 森林/湿地/草原/高山")
    lat = Column(Float, comment="纬度")
    lng = Column(Float, comment="经度")
    vegetation_coverage = Column(Float, comment="植被覆盖度(%)")
    species_richness = Column(Integer, comment="物种丰富度(种)")
    species_diversity_index = Column(Float, comment="香农多样性指数")
    water_quality_index = Column(Float, comment="水质指数(0-100)")
    soil_health_index = Column(Float, comment="土壤健康指数(0-100)")
    air_quality_index = Column(Float, comment="空气质量指数")
    carbon_sequestration = Column(Float, comment="碳汇量(tCO2e/年)")
    ecological_health_score = Column(Float, comment="综合生态健康评分(0-100)")
    anomaly_flag = Column(Boolean, default=False, comment="是否异常")
    recorded_at = Column(DateTime, default=datetime.datetime.now, comment="记录时间")
    extra_data = Column(JSON, comment="扩展数据")


class FireRiskAssessment(Base):
    __tablename__ = "fire_risk_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_name = Column(String(100), comment="区域名称")
    lat = Column(Float)
    lng = Column(Float)
    risk_level = Column(String(20), comment="风险等级: low/medium/high/extreme")
    risk_score = Column(Float, comment="风险评分(0-100)")
    temperature = Column(Float, comment="气温(°C)")
    humidity = Column(Float, comment="湿度(%)")
    wind_speed = Column(Float, comment="风速(m/s)")
    wind_direction = Column(String(10), comment="风向")
    vegetation_type = Column(String(50), comment="植被类型")
    drought_index = Column(Float, comment="干旱指数")
    historical_fire_count = Column(Integer, comment="历史火灾次数")
    predicted_at = Column(DateTime, default=datetime.datetime.now)
    patrol_routes = Column(JSON, comment="巡护路线规划")


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(50), comment="预警类型: fire/pest/invasive/human/flood")
    alert_level = Column(String(20), comment="预警等级: blue/yellow/orange/red")
    title = Column(String(200), comment="预警标题")
    description = Column(Text, comment="预警描述")
    zone_name = Column(String(100))
    lat = Column(Float)
    lng = Column(Float)
    probability = Column(Float, comment="发生概率")
    estimated_impact = Column(Float, comment="预计影响范围(km²)")
    suggested_actions = Column(JSON, comment="建议措施")
    response_plan = Column(Text, comment="应急预案")
    is_active = Column(Boolean, default=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)


class ResourceSchedule(Base):
    __tablename__ = "resource_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patrol_team = Column(String(100), comment="巡护队伍")
    team_size = Column(Integer, comment="队伍人数")
    zone_name = Column(String(100), comment="负责区域")
    route_points = Column(JSON, comment="巡护路线坐标点")
    vehicles = Column(JSON, comment="配备车辆")
    equipment = Column(JSON, comment="配备装备")
    schedule_date = Column(DateTime, comment="调度日期")
    shift = Column(String(20), comment="班次: morning/afternoon/night")
    status = Column(String(20), default="scheduled", comment="状态: scheduled/in_progress/completed")
    created_at = Column(DateTime, default=datetime.datetime.now)


class VisitorFlow(Base):
    __tablename__ = "visitor_flows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    zone_name = Column(String(100))
    visitor_count = Column(Integer, comment="游客数量")
    capacity = Column(Integer, comment="承载能力上限")
    congestion_level = Column(Float, comment="拥堵指数(0-1)")
    recorded_at = Column(DateTime, default=datetime.datetime.now)


class PatrolLog(Base):
    __tablename__ = "patrol_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String(100))
    zone_name = Column(String(100))
    start_time = Column(DateTime)
    end_time = Column(DateTime, nullable=True)
    route_actual = Column(JSON, comment="实际路线")
    findings = Column(JSON, comment="巡查发现")
    status = Column(String(20), default="active")


class ParkZone(Base):
    __tablename__ = "park_zones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True)
    zone_type = Column(String(50), comment="区域类型")
    lat = Column(Float, default=0.0, comment="中心纬度")
    lng = Column(Float, default=0.0, comment="中心经度")
    boundary = Column(JSON, comment="边界坐标点")
    area_km2 = Column(Float, comment="面积(km²)")
    description = Column(Text)
    core_protection = Column(Boolean, default=False, comment="核心保护区")
    restriction_level = Column(String(20), comment="限制等级")
