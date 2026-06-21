import random
import datetime
from app.database import SessionLocal, engine, Base
from app.models.models import (
    EcologicalIndicator, FireRiskAssessment, RiskAlert,
    ResourceSchedule, VisitorFlow, ParkZone, PatrolLog
)
from app.utils.park_zones import PARK_ZONES
from app.services.weather_service import fetch_all_weather
from app.services.external_aqi import fetch_all_aqi
from app.services.external_firms import fetch_all_fire_counts
from app.config import settings

ANIMAL_SPECIES = ["藏羚羊", "大熊猫", "东北虎", "雪豹", "藏狐", "黑颈鹤", "藏野驴",
                   "金丝猴", "朱鹮", "羚牛", "野牦牛", "旱獭", "梅花鹿", "白唇鹿",
                   "马鹿", "岩羊", "斑尾榛鸡", "雪鸡", "黑熊", "棕熊"]

PLANT_SPECIES = ["云杉", "冷杉", "高原嵩草", "紫花针茅", "矮生嵩草", "圆穗蓼",
                  "杜鹃", "箭竹", "高山柳", "金露梅"]

PATROL_TEAMS = ["巡护一队", "巡护二队", "巡护三队", "无人机巡检队", "科研监测队"]
VEHICLE_TYPES = ["全地形车", "巡护皮卡", "摩托车", "无人机", "马匹"]
EQUIPMENT_TYPES = ["GPS定位仪", "红外相机", "望远镜", "灭火器", "急救包", "对讲机", "水文监测仪"]


def init_db():
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")


def generate_park_zones():
    db = SessionLocal()
    try:
        if db.query(ParkZone).count() > 0:
            return
        for z in PARK_ZONES:
            zone = ParkZone(**z)
            db.add(zone)
        db.commit()
        print(f"已生成 {len(PARK_ZONES)} 个园区区域")
    finally:
        db.close()


def generate_ecological_data(days: int = 30):
    db = SessionLocal()
    try:
        db.query(EcologicalIndicator).delete()
        weather_data = fetch_all_weather()
        aqi_data = fetch_all_aqi()
        now = datetime.datetime.now()
        records = []
        for i in range(days):
            for z in PARK_ZONES:
                hour = 8 + (i % 8)
                recorded = now - datetime.timedelta(days=days - i, hours=random.randint(0, 12))
                base_health = random.uniform(60, 95)
                anomaly = random.random() < 0.05
                if anomaly:
                    base_health -= random.uniform(15, 40)

                veg = min(100, max(10, base_health + random.uniform(-5, 5)))
                species_count = int(base_health * 0.8 + random.randint(-10, 10))
                diversity = round(max(0.5, min(4.5, base_health / 25 + random.uniform(-0.3, 0.3))), 2)
                water = min(100, max(20, base_health + random.uniform(-10, 10)))
                soil = min(100, max(20, base_health + random.uniform(-5, 15)))

                aqi_info = aqi_data.get(z["name"], {})
                real_aqi = aqi_info.get("air_quality_index")
                aqi_source = aqi_info.get("source", "random")
                if real_aqi is not None:
                    air_qual = round(real_aqi + random.uniform(-5, 5), 1)
                    air_qual = min(100, max(0, air_qual))
                else:
                    air_qual = round(random.uniform(30, 95), 1)

                records.append(EcologicalIndicator(
                    zone_name=z["name"],
                    zone_type=z["zone_type"],
                    lat=z["lat"], lng=z["lng"],
                    vegetation_coverage=round(veg, 1),
                    species_richness=max(1, species_count),
                    species_diversity_index=diversity,
                    water_quality_index=round(water, 1),
                    soil_health_index=round(soil, 1),
                    air_quality_index=air_qual,
                    carbon_sequestration=round(random.uniform(100, 5000), 1),
                    ecological_health_score=round(max(0, min(100, base_health)), 1),
                    anomaly_flag=anomaly,
                    recorded_at=recorded,
                    extra_data={"dominant_species": random.sample(ANIMAL_SPECIES, 3),
                                 "weather": weather_data.get(z["name"], {}).get("weather_cn", random.choice(["晴", "多云", "小雨", "阴"])),
                                 "aqi_source": aqi_source}
                ))
        db.add_all(records)
        db.commit()
        print(f"已生成 {len(records)} 条生态指标数据")
    finally:
        db.close()


def generate_fire_risk_data():
    db = SessionLocal()
    try:
        db.query(FireRiskAssessment).delete()
        now = datetime.datetime.now()
        weather_data = fetch_all_weather()
        fire_counts = fetch_all_fire_counts(api_key=settings.FIRMS_MAP_KEY)
        records = []
        for z in PARK_ZONES:
            w = weather_data.get(z["name"], {})
            temp = w.get("temperature", round(random.uniform(15, 38), 1))
            hum = w.get("humidity", round(random.uniform(20, 80), 1))
            wind = w.get("wind_speed", round(random.uniform(1, 25), 1))
            wind_dir = w.get("wind_direction", random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]))
            drought = round(random.uniform(0, 100), 1)
            risk = min(100, (temp * 1.5 + (100 - hum) * 0.8 + wind * 1.2 + drought * 0.5) / 4 + random.uniform(-10, 10))

            level = "low"
            if risk > 70:
                level = "extreme"
            elif risk > 50:
                level = "high"
            elif risk > 30:
                level = "medium"

            patrol = [[z["lat"] + random.uniform(-0.1, 0.1), z["lng"] + random.uniform(-0.1, 0.1)]
                      for _ in range(random.randint(3, 6))]

            fc = fire_counts.get(z["name"], {})
            real_count = fc.get("historical_fire_count")
            fire_source = fc.get("source", "random")
            if real_count is not None:
                hist_fire = real_count
            else:
                hist_fire = random.randint(0, 5)

            records.append(FireRiskAssessment(
                zone_name=z["name"],
                lat=z["lat"], lng=z["lng"],
                risk_level=level,
                risk_score=round(risk, 1),
                temperature=temp, humidity=hum,
                wind_speed=wind,
                wind_direction=wind_dir,
                vegetation_type=random.choice(["针叶林", "阔叶林", "灌丛", "草原", "高山草甸"]),
                drought_index=drought,
                historical_fire_count=hist_fire,
                predicted_at=now - datetime.timedelta(hours=random.randint(1, 6)),
                patrol_routes=patrol,
            ))
        db.add_all(records)
        db.commit()
        print(f"已生成 {len(records)} 条火灾风险评估数据")
    finally:
        db.close()


def generate_risk_alerts():
    db = SessionLocal()
    try:
        db.query(RiskAlert).delete()
        now = datetime.datetime.now()
        alert_types = ["fire", "pest", "invasive", "human", "flood"]
        levels = ["blue", "yellow", "orange", "red"]
        titles = {
            "fire": ["高温干旱火险预警", "雷电引发火灾风险", "游客用火隐患"],
            "pest": ["松材线虫病扩散预警", "蝗虫灾害预警", "森林病虫害高发"],
            "invasive": ["外来物种扩散预警", "加拿大一枝黄花入侵"],
            "human": ["游客违规进入核心区", "非法采集植物预警"],
            "flood": ["暴雨引发山洪预警", "融雪性洪水风险"],
        }

        records = []
        for i in range(45):
            at = random.choice(alert_types)
            lv = random.choice(levels)
            z = random.choice(PARK_ZONES)
            title = random.choice(titles.get(at, ["一般预警"]))

            records.append(RiskAlert(
                alert_type=at, alert_level=lv,
                title=title,
                description=f"{z['name']}发生{title}，根据监测数据分析存在一定风险，建议加强巡查。",
                zone_name=z["name"],
                lat=z["lat"] + random.uniform(-0.05, 0.05),
                lng=z["lng"] + random.uniform(-0.05, 0.05),
                probability=round(random.uniform(10, 95), 1),
                estimated_impact=round(random.uniform(0.5, 50), 1),
                suggested_actions=[
                    "加强无人机巡检频次",
                    "通知附近巡护队就位",
                    "准备应急物资",
                    "上报管理局指挥中心"
                ],
                response_plan=f"针对{title}的一级响应预案：立即派遣{random.choice(PATROL_TEAMS)}前往现场处置，"
                              f"启动{lv}级应急响应机制。",
                is_active=random.choice([True, True, True, False]),
                created_at=now - datetime.timedelta(hours=random.randint(1, 168)),
            ))
        db.add_all(records)
        db.commit()
        print(f"已生成 {len(records)} 条风险预警数据")
    finally:
        db.close()


def generate_resources():
    db = SessionLocal()
    try:
        db.query(ResourceSchedule).delete()
        now = datetime.datetime.now()
        records = []
        for i in range(20):
            z = random.choice(PARK_ZONES)
            team = random.choice(PATROL_TEAMS)
            route = [[z["lat"] + random.uniform(-0.08, 0.08), z["lng"] + random.uniform(-0.08, 0.08)]
                     for _ in range(random.randint(4, 8))]

            records.append(ResourceSchedule(
                patrol_team=team,
                team_size=random.randint(3, 8),
                zone_name=z["name"],
                route_points=route,
                vehicles=random.sample(VEHICLE_TYPES, k=random.randint(1, 3)),
                equipment=random.sample(EQUIPMENT_TYPES, k=random.randint(2, 5)),
                schedule_date=now + datetime.timedelta(days=random.randint(0, 3),
                                                        hours=random.randint(0, 12)),
                shift=random.choice(["morning", "afternoon", "night"]),
                status=random.choice(["scheduled", "in_progress", "completed"]),
            ))
        db.add_all(records)
        db.commit()
        print(f"已生成 {len(records)} 条资源调度数据")
    finally:
        db.close()


def generate_visitor_data():
    db = SessionLocal()
    try:
        db.query(VisitorFlow).delete()
        now = datetime.datetime.now()
        records = []
        for i in range(24):
            for z in random.sample(PARK_ZONES, 4):
                capacity = int(z["area_km2"] * random.uniform(0.5, 2))
                visitors = int(capacity * random.uniform(0.1, 0.95))
                records.append(VisitorFlow(
                    zone_name=z["name"],
                    visitor_count=visitors,
                    capacity=capacity,
                    congestion_level=round(visitors / capacity, 2),
                    recorded_at=now - datetime.timedelta(hours=i),
                ))
        db.add_all(records)
        db.commit()
        print(f"已生成 {len(records)} 条游客流量数据")
    finally:
        db.close()


def generate_all_mock_data():
    init_db()
    generate_park_zones()
    generate_ecological_data(30)
    generate_fire_risk_data()
    generate_risk_alerts()
    generate_resources()
    generate_visitor_data()
    print("\n===== 所有模拟数据生成完毕 =====")


if __name__ == "__main__":
    generate_all_mock_data()
