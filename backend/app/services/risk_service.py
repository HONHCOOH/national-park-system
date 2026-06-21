import random
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from app.models.models import RiskAlert


class RiskService:

    @staticmethod
    def get_active_alerts(db: Session):
        return db.query(RiskAlert).filter(
            RiskAlert.is_active == True,
            RiskAlert.is_resolved == False,
        ).order_by(desc(RiskAlert.created_at)).all()

    @staticmethod
    def get_alert_history(db: Session, limit: int = 20):
        return db.query(RiskAlert).order_by(desc(RiskAlert.created_at)).limit(limit).all()

    @staticmethod
    def get_alerts_by_level(db: Session, level: str):
        return db.query(RiskAlert).filter(
            RiskAlert.alert_level == level,
            RiskAlert.is_active == True,
        ).all()

    @staticmethod
    def resolve_alert(db: Session, alert_id: int):
        alert = db.query(RiskAlert).filter(RiskAlert.id == alert_id).first()
        if alert:
            alert.is_resolved = True
            alert.is_active = False
            alert.resolved_at = datetime.now()
            db.commit()
            return {"success": True, "alert_id": alert_id}
        return {"success": False, "error": "预警不存在"}

    @staticmethod
    def generate_response_plan(alert_type: str, alert_level: str, zone_name: str):
        level_actions = {
            "red": ["立即启动最高级别应急响应", "全员进入紧急状态", "通知上级主管部门", "组织人员撤离"],
            "orange": ["启动二级应急响应", "相关巡护队就位", "应急物资前置", "加强重点区域监测"],
            "yellow": ["启动三级预警", "增加巡护频次", "准备应急物资", "通知相关区域负责人"],
            "blue": ["加强监测", "定期通报情况", "检查应急设备", "更新应急预案"],
        }
        type_actions = {
            "fire": ["检查防火隔离带", "预置灭火器材", "控制火源", "无人机实时监测"],
            "pest": ["喷洒生物农药", "设置诱捕装置", "清除病木", "设立检疫点"],
            "invasive": ["物理清除外来物种", "喷洒除草剂", "设置拦截网", "加强边界巡查"],
            "human": ["设置警示标识", "加强边界巡护", "劝返违规人员", "启动法律程序"],
            "flood": ["疏通排水系统", "加固堤坝", "转移低洼区域物资", "监测水位变化"],
        }

        actions = level_actions.get(alert_level, level_actions["blue"]) + \
                  type_actions.get(alert_type, type_actions["fire"])

        return {
            "alert_type": alert_type,
            "alert_level": alert_level,
            "zone": zone_name,
            "immediate_actions": actions[:3],
            "follow_up_actions": actions[3:],
            "estimated_resolution_time": {
                "red": "2小时内",
                "orange": "6小时内",
                "yellow": "24小时内",
                "blue": "48小时内",
            }.get(alert_level, "48小时内"),
        }

    @staticmethod
    def get_timeline_data(db: Session, limit: int = 50):
        alerts = db.query(RiskAlert).order_by(RiskAlert.created_at.desc()).limit(limit).all()
        alerts_sorted = sorted(alerts, key=lambda a: a.created_at)
        return [{
            "id": a.id,
            "time": a.created_at.isoformat() if a.created_at else None,
            "title": a.title,
            "type": a.alert_type,
            "level": a.alert_level,
            "zone_name": a.zone_name,
            "description": a.description[:80] if a.description else "",
            "is_resolved": a.is_resolved,
        } for a in alerts_sorted]

    @staticmethod
    def get_alert_stats(db: Session):
        total = db.query(RiskAlert).count()
        active = db.query(RiskAlert).filter(RiskAlert.is_active == True).count()
        by_level = db.query(
            RiskAlert.alert_level,
            RiskAlert.alert_type,
        ).filter(RiskAlert.is_active == True).all()

        levels = {"red": 0, "orange": 0, "yellow": 0, "blue": 0}
        types = {}
        for lv, tp in by_level:
            levels[lv] = levels.get(lv, 0) + 1
            types[tp] = types.get(tp, 0) + 1

        return {
            "total_alerts": total,
            "active_alerts": active,
            "by_level": levels,
            "by_type": types,
        }


risk_service = RiskService()
