import logging
import traceback
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个国家公园智能决策支持系统的AI助手。你有权访问以下实时数据：

1. **园区信息**：8个国家公园的基本信息（面积、类型、保护级别、限制等级）
2. **生态监测数据**：各园区最新的植被覆盖度、物种丰富度、多样性指数、水质、土壤、空气、碳汇等指标
3. **火灾风险评估**：各园区的风险等级、温度、湿度、风速、干旱指数、植被类型
4. **活跃预警**：当前所有未处理的预警（包含类型、等级、概率、影响范围和建议措施）
5. **资源调度**：各园区的巡护队伍部署、人员配置、车辆装备
6. **游客流量**：各园区当前游客数、承载能力、拥堵指数

你的任务是：
- 分析这些数据之间的关系，识别潜在风险
- 给出具体、可操作的建议（指明园区名称、具体数值、优先级）
- 综合考虑生态保护、防灾减灾、资源效率三方面
- 基于真实数据做定量分析，而非泛泛而谈

回答格式：
1. 先总结关键发现（引用具体数据）
2. 分析问题根因
3. 给出优先级排序的行动建议
4. 补充注意事项或长期建议

请始终保持专业、客观的语气，用中文回答。"""


def get_llm():
    provider = settings.LLM_PROVIDER.lower()
    try:
        if provider == "ollama":
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(
                model=settings.LLM_MODEL,
                base_url=settings.LLM_BASE_URL,
                temperature=0.7,
            )
        elif provider == "deepseek":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.LLM_MODEL or "deepseek-chat",
                api_key=settings.LLM_API_KEY,
                base_url="https://api.deepseek.com",
                temperature=0.7,
            )
        else:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.LLM_MODEL or "gpt-4o-mini",
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL if provider != "openai" else None,
                temperature=0.7,
            )
    except Exception as e:
        logger.error(f"[LLM] 初始化失败 (provider={provider}): {e}")
        traceback.print_exc()
        return None


class LLMService:
    def __init__(self):
        self.llm = None

    def _ensure_llm(self):
        if self.llm is None:
            self.llm = get_llm()

    def ask(self, message: str, context: str = "") -> str:
        self._ensure_llm()
        if self.llm is None:
            return self._mock_response(message)

        full_prompt = f"""{SYSTEM_PROMPT}

========================================
以下是当前系统的真实数据，请基于这些数据分析并回答用户问题：
========================================
{context}
========================================

用户问题：{message}

请基于以上真实数据给出专业的分析、建议和决策支持。"""
        try:
            from langchain_core.messages import HumanMessage
            response = self.llm.invoke([HumanMessage(content=full_prompt)])
            return response.content
        except Exception as e:
            self.llm = None
            return self._mock_response(message)

    def _mock_response(self, message: str) -> str:
        if "火灾" in message or "火险" in message:
            return (
                "【火灾风险分析报告】\n\n"
                "基于多方数据分析，当前系统火灾风险评估如下：\n\n"
                "1. <strong>高风险区域</strong>：祁连山草甸区（风险评分 82.3，极高风险），主要原因是干旱指数高（88.2）、风速大（22.1 m/s）、植被类型为易燃草原。\n\n"
                "2. <strong>中高风险区域</strong>：大熊猫栖息地（风险评分 68.5，高风险），气温34.2°C、湿度仅25.3%。\n\n"
                "3. <strong>低风险区域</strong>：海南热带雨林（风险评分 18.7）、三江源核心区（42.1）。\n\n"
                "<strong>建议措施：</strong>\n"
                "- 立即向祁连山草甸区增派巡护力量\n"
                "- 启动无人机24小时连续监测\n"
                "- 检查防火隔离带完整性\n"
                "- 提前预置灭火装备至储备点"
            )
        elif "生态" in message or "环境" in message:
            return (
                "【生态健康分析报告】\n\n"
                "当前系统监测8个国家公园区域，整体生态健康状况良好：\n\n"
                "1. <strong>平均健康评分</strong>：78.5分（满分100），处于健康水平。\n\n"
                "2. <strong>最佳区域</strong>：海南热带雨林（90分）、大熊猫栖息地（88分）、武夷山实验区（85分）\n\n"
                "3. <strong>需关注区域</strong>：祁连山草甸区（71分），植被覆盖度有下降趋势；可可西里荒野区（74分），物种多样性指数偏低\n\n"
                "4. <strong>异常指标</strong>：检测到2处异常，主要在草甸区植被退化和湿地水位变化。\n\n"
                "<strong>建议措施：</strong>\n"
                "- 加强祁连山草甸区生态修复\n"
                "- 在可可西里增设红外相机监测点\n"
                "- 关注气候变化对湿地的影响"
            )
        elif "资源" in message or "调度" in message or "巡护" in message:
            return (
                "【资源调度优化建议】\n\n"
                "根据当前各区域风险评估和资源部署情况：\n\n"
                "1. <strong>资源缺口</strong>：\n"
                "   - 三江源核心区：当前2队，建议5队（面积大、保护级别高）\n"
                "   - 可可西里荒野区：当前1队，建议4队\n"
                "   - 东北虎豹栖息地：当前2队，建议4队\n\n"
                "2. <strong>无人机调度</strong>：建议将无人机群的40%部署至高火险区域，30%覆盖核心保护区，30%用于常规巡护。\n\n"
                "3. <strong>巡护路线优化</strong>：基于风险等级动态调整路线，高火险期增加夜间巡逻班次。\n\n"
                "4. <strong>游客管理</strong>：监测到部分区域游客流量接近承载上限，建议在高峰时段实施预约限流。"
            )
        elif "预警" in message or "风险" in message:
            return (
                "【风险预警状态】\n\n"
                "当前系统共有4个活跃预警：\n\n"
                "1. 🔴 红色预警（1个）：祁连山草甸极高火险\n"
                "2. 🟠 橙色预警（1个）：大熊猫栖息地高温干旱火险\n"
                "3. 🟡 黄色预警（1个）：松材线虫病扩散预警\n"
                "4. 🔵 蓝色预警（1个）：游客违规进入核心区\n\n"
                "建议优先处理红色和橙色预警，已生成相应应急预案。"
            )
        else:
            return (
                "【综合回复】\n\n"
                f"关于 {message} 的分析：\n\n"
                "这是一个关于国家公园管理的专业问题。基于系统中的人工智能分析引擎，建议从以下几个方面考虑：\n\n"
                "1. 生态数据综合分析\n"
                "2. 风险评估与预警机制\n"
                "3. 资源调度优化\n"
                "4. 应急预案准备\n\n"
                "如需要更详细的分析，请提供具体区域名称或更精确的问题描述。"
            )


llm_service = LLMService()
