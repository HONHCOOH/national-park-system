import random
import math
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.models import ResourceSchedule, VisitorFlow, ParkZone, PatrolLog


class ResourceService:

    @staticmethod
    def get_schedules(db: Session, limit: int = 20):
        return db.query(ResourceSchedule).order_by(
            desc(ResourceSchedule.schedule_date)
        ).limit(limit).all()

    @staticmethod
    def get_schedules_by_zone(db: Session, zone_name: str):
        return db.query(ResourceSchedule).filter(
            ResourceSchedule.zone_name == zone_name
        ).order_by(desc(ResourceSchedule.schedule_date)).limit(10).all()

    @staticmethod
    def create_schedule(db: Session, data: dict):
        schedule = ResourceSchedule(**data)
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule

    @staticmethod
    def get_visitor_stats(db: Session):
        zones_list = db.query(VisitorFlow.zone_name).distinct().all()
        result = []
        for (zone_name,) in zones_list:
            latest = db.query(VisitorFlow).filter(
                VisitorFlow.zone_name == zone_name
            ).order_by(desc(VisitorFlow.recorded_at)).first()
            if not latest:
                continue
            recent = db.query(VisitorFlow).filter(
                VisitorFlow.zone_name == zone_name
            ).order_by(desc(VisitorFlow.recorded_at)).limit(24).all()
            avg_visitors = sum(r.visitor_count for r in recent) / len(recent) if recent else latest.visitor_count
            result.append({
                "zone_name": zone_name,
                "current_visitors": latest.visitor_count,
                "capacity": latest.capacity,
                "congestion": latest.congestion_level,
                "avg_visitors_24h": round(avg_visitors, 0),
                "needs_restriction": latest.congestion_level > 0.8,
            })
        return result

    @staticmethod
    def optimize_allocation(db: Session):
        zones = db.query(ParkZone).all()
        schedules = db.query(ResourceSchedule).filter(
            ResourceSchedule.status.in_(["scheduled", "in_progress"])
        ).all()

        allocation = []
        for z in zones:
            zone_schedules = [s for s in schedules if s.zone_name == z.name]
            team_count = len(zone_schedules)
            total_personnel = sum(s.team_size for s in zone_schedules)

            risk_multiplier = 1.0
            if z.core_protection:
                risk_multiplier = 2.0
            elif z.restriction_level == "strict":
                risk_multiplier = 1.5

            suggested_teams = max(1, math.ceil(z.area_km2 / 300 * risk_multiplier))

            allocation.append({
                "zone_name": z.name,
                "area_km2": z.area_km2,
                "current_teams": team_count,
                "current_personnel": total_personnel,
                "suggested_teams": suggested_teams,
                "suggested_personnel": suggested_teams * 5,
                "gap": suggested_teams - team_count,
                "priority": "high" if suggested_teams > team_count else "normal",
            })

        allocation.sort(key=lambda x: x["gap"], reverse=True)
        return allocation

    @staticmethod
    def get_resource_flow(db: Session):
        schedules = db.query(ResourceSchedule).filter(
            ResourceSchedule.status.in_(["scheduled", "in_progress"])
        ).all()

        nodes_set = {}
        links_data = []

        def get_node(name):
            if name not in nodes_set:
                nodes_set[name] = len(nodes_set)
            return nodes_set[name]

        for s in schedules:
            team_node = s.patrol_team
            zone_node = s.zone_name
            get_node(team_node)
            get_node(zone_node)
            links_data.append({
                "source": team_node,
                "target": zone_node,
                "value": s.team_size,
            })

            for v in (s.vehicles or []):
                vn = f"[车辆]{v}"
                get_node(vn)
                links_data.append({"source": vn, "target": zone_node, "value": 1})

            for e in (s.equipment or []):
                en = f"[装备]{e}"
                get_node(en)
                links_data.append({"source": en, "target": zone_node, "value": 1})

        aggregated = {}
        for l in links_data:
            key = (l["source"], l["target"])
            if key not in aggregated:
                aggregated[key] = l["value"]
            else:
                aggregated[key] += l["value"]

        links = [{"source": src, "target": tgt, "value": val} for (src, tgt), val in aggregated.items()]
        nodes = [{"name": n, "id": i} for n, i in nodes_set.items()]

        return {"nodes": nodes, "links": links}

    @staticmethod
    def get_patrol_logs(db: Session, limit: int = 10):
        return db.query(PatrolLog).order_by(desc(PatrolLog.start_time)).limit(limit).all()


resource_service = ResourceService()
