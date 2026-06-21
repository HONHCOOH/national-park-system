from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.models.models import (
    ParkZone, EcologicalIndicator, FireRiskAssessment,
    RiskAlert, ResourceSchedule, VisitorFlow, PatrolLog
)


class ContextService:

    @staticmethod
    def build_full_context(db: Session) -> str:
        parts = []
        parts.append(ContextService._zones_context(db))
        parts.append(ContextService._ecology_context(db))
        parts.append(ContextService._fire_context(db))
        parts.append(ContextService._alert_context(db))
        parts.append(ContextService._resource_context(db))
        parts.append(ContextService._visitor_context(db))
        return "\n\n".join(parts)

    @staticmethod
    def _zones_context(db: Session) -> str:
        zones = db.query(ParkZone).all()
        if not zones:
            return ""

        lines = ["【国家公园区域信息】"]
        for z in zones:
            prot = "核心保护区" if z.core_protection else "一般保护区"
            res = {"strict": "严格限制", "moderate": "适度限制", "open": "开放"}.get(z.restriction_level, z.restriction_level)
            lines.append(
                f"- {z.name}：{z.zone_type}，面积{z.area_km2}km²，{prot}，限制等级：{res}，{z.description}"
            )
        return "\n".join(lines)

    @staticmethod
    def _ecology_context(db: Session) -> str:
        # 获取每个园区最新的生态指标
        sub = db.query(
            EcologicalIndicator.zone_name,
            func.max(EcologicalIndicator.recorded_at).label("max_time")
        ).group_by(EcologicalIndicator.zone_name).subquery()

        records = db.query(EcologicalIndicator).join(
            sub,
            (EcologicalIndicator.zone_name == sub.c.zone_name) &
            (EcologicalIndicator.recorded_at == sub.c.max_time)
        ).all()

        if not records:
            return ""

        lines = ["【生态监测最新数据】"]
        for r in records:
            anomaly = " ⚠异常" if r.anomaly_flag else ""
            lines.append(
                f"- {r.zone_name}：生态健康评分{r.ecological_health_score:.1f}/100，"
                f"植被覆盖度{r.vegetation_coverage:.1f}%，物种丰富度{r.species_richness}种，"
                f"香农多样性指数{r.species_diversity_index:.2f}，"
                f"水质{r.water_quality_index:.1f}，土壤{r.soil_health_index:.1f}，"
                f"空气质量{r.air_quality_index:.1f}，碳汇量{r.carbon_sequestration:.1f}tCO2e/年{anomaly}"
            )
        return "\n".join(lines)

    @staticmethod
    def _fire_context(db: Session) -> str:
        risks = db.query(FireRiskAssessment).order_by(
            desc(FireRiskAssessment.risk_score)
        ).all()

        if not risks:
            return ""

        lines = ["【火灾风险评估】"]
        level_cn = {"extreme": "极高", "high": "高", "medium": "中", "low": "低"}
        for r in risks:
            vtype = r.vegetation_type or "未知"
            lines.append(
                f"- {r.zone_name}：风险等级{level_cn.get(r.risk_level, r.risk_level)}，"
                f"风险评分{r.risk_score:.1f}/100，温度{r.temperature:.1f}°C，"
                f"湿度{r.humidity:.1f}%，风速{r.wind_speed:.1f}m/s，"
                f"干旱指数{r.drought_index:.1f}，植被类型{vtype}，"
                f"历史火灾{r.historical_fire_count}次"
            )
        return "\n".join(lines)

    @staticmethod
    def _alert_context(db: Session) -> str:
        alerts = db.query(RiskAlert).filter(
            RiskAlert.is_active == True,
            RiskAlert.is_resolved == False,
        ).order_by(desc(RiskAlert.created_at)).all()

        if not alerts:
            return ""

        lines = ["【当前活跃预警】"]
        level_cn = {"red": "🔴红色", "orange": "🟠橙色", "yellow": "🟡黄色", "blue": "🔵蓝色"}
        type_cn = {"fire": "火灾", "pest": "病虫害", "invasive": "入侵物种", "human": "人为活动", "flood": "洪涝"}
        for a in alerts:
            actions = "、".join(a.suggested_actions[:3]) if a.suggested_actions else "无"
            lines.append(
                f"- [{level_cn.get(a.alert_level, a.alert_level)}] {a.title}（{type_cn.get(a.alert_type, a.alert_type)}）\n"
                f"  区域：{a.zone_name}，概率：{a.probability:.1f}%，预计影响{a.estimated_impact:.1f}km²\n"
                f"  描述：{a.description}\n"
                f"  建议措施：{actions}"
            )
        return "\n".join(lines)

    @staticmethod
    def _resource_context(db: Session) -> str:
        schedules = db.query(ResourceSchedule).filter(
            ResourceSchedule.status.in_(["scheduled", "in_progress"])
        ).order_by(desc(ResourceSchedule.schedule_date)).limit(15).all()

        if not schedules:
            return ""

        shift_cn = {"morning": "早班", "afternoon": "午班", "night": "晚班"}
        lines = ["【当前资源调度情况】"]

        zone_teams = {}
        for s in schedules:
            z = s.zone_name
            if z not in zone_teams:
                zone_teams[z] = {"teams": [], "personnel": 0}
            zone_teams[z]["teams"].append(s.patrol_team)
            zone_teams[z]["personnel"] += s.team_size

        for zone_name, info in zone_teams.items():
            teams_str = "、".join(info["teams"])
            lines.append(
                f"- {zone_name}：{len(info['teams'])}支队伍（{teams_str}），共{info['personnel']}人"
            )

        vehicles_all = set()
        for s in schedules:
            if s.vehicles:
                vehicles_all.update(s.vehicles)
        lines.append(f"\n可用车辆类型：{'、'.join(sorted(vehicles_all)) if vehicles_all else '无'}")

        equipment_all = set()
        for s in schedules:
            if s.equipment:
                equipment_all.update(s.equipment)
        lines.append(f"可用装备类型：{'、'.join(sorted(equipment_all)) if equipment_all else '无'}")

        return "\n".join(lines)

    @staticmethod
    def _visitor_context(db: Session) -> str:
        zones_list = db.query(VisitorFlow.zone_name).distinct().all()
        if not zones_list:
            return ""

        lines = ["【游客流量统计】"]
        for (zone_name,) in zones_list:
            latest = db.query(VisitorFlow).filter(
                VisitorFlow.zone_name == zone_name
            ).order_by(desc(VisitorFlow.recorded_at)).first()
            if not latest:
                continue
            congest = "🔴需限流" if latest.congestion_level > 0.8 else ("🟡较拥挤" if latest.congestion_level > 0.6 else "🟢正常")
            lines.append(
                f"- {zone_name}：当前{latest.visitor_count}人，承载上限{latest.capacity}人，"
                f"拥堵指数{latest.congestion_level:.0%}，{congest}"
            )

        patrol_logs = db.query(PatrolLog).filter(
            PatrolLog.status == "active"
        ).order_by(desc(PatrolLog.start_time)).limit(5).all()
        if patrol_logs:
            lines.append("\n【当前巡护日志】")
            for pl in patrol_logs:
                findings_str = ""
                if pl.findings:
                    findings_str = f"，发现：{'、'.join(pl.findings[:3])}"
                lines.append(
                    f"- {pl.team_name} → {pl.zone_name}，"
                    f"开始时间{pl.start_time.strftime('%m/%d %H:%M')}{findings_str}"
                )

        return "\n".join(lines)


context_service = ContextService()
