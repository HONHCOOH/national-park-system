import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Polygon
import numpy as np

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = 'diagrams'
BLACK = '#000000'
WHITE = '#FFFFFF'
LW = 1.2
FONT_TITLE = 18
FONT_BODY = 9.5
FONT_SMALL = 8

BOX_KW = dict(boxstyle="square,pad=0.3", facecolor=WHITE, edgecolor=BLACK, linewidth=LW)
DIAMOND_KW = dict(facecolor=WHITE, edgecolor=BLACK, linewidth=LW)


def save_fig(fig, name):
    fig.savefig(f'{OUTPUT_DIR}/{name}.png', dpi=200, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f'  [OK] {name}.png')


def draw_box(ax, x, y, w, h):
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h, **BOX_KW)
    ax.add_patch(rect)
    return rect


def draw_circle(ax, x, y, r):
    c = Circle((x, y), r, facecolor=WHITE, edgecolor=BLACK, linewidth=LW)
    ax.add_patch(c)
    return c


def draw_diamond(ax, x, y, w, h):
    points = np.array([
        [x, y + h/2],
        [x + w/2, y],
        [x, y - h/2],
        [x - w/2, y],
    ])
    d = Polygon(points, **DIAMOND_KW)
    ax.add_patch(d)
    return d


def add_arrow(ax, x1, y1, x2, y2, lw=1.2, style='->'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=BLACK, lw=lw))


def add_line(ax, x1, y1, x2, y2, lw=0.8, style='-'):
    ax.plot([x1, x2], [y1, y2], color=BLACK, lw=lw, linestyle=style)


# ============================================================
# 图1: 系统整体架构图
# ============================================================
def draw_architecture():
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_facecolor('white')

    ax.text(6, 8.6, '系统整体架构图', ha='center', va='center', fontsize=FONT_TITLE, fontweight='bold', color=BLACK)

    # Four horizontal layers
    layers = [
        (0.3, 6.3, 11.4, 1.5, '表现层 (Presentation Layer)\nVue 3 + Element Plus + Vite | ECharts | Leaflet | Axios'),
        (0.3, 4.5, 11.4, 1.5, '业务逻辑层 (Business Logic Layer)\nFastAPI + Uvicorn | 六大路由模块 | 服务层'),
        (0.3, 2.7, 11.4, 1.5, '数据访问层 (Data Access Layer)\nSQLAlchemy ORM 2.0 | SessionLocal'),
        (0.3, 0.9, 11.4, 1.5, '数据存储层 (Data Storage Layer)\nSQLite | Redis (可选)'),
    ]

    for lx, ly, lw, lh, label in layers:
        draw_box(ax, lx + lw/2, ly + lh/2, lw, lh)
        ax.text(lx + lw/2, ly + lh/2, label, ha='center', va='center', fontsize=11, color=BLACK)

    # LLM box on the right
    draw_box(ax, 10.6, 4.6, 2.2, 4.8)
    ax.text(10.6, 6.8, '大模型服务层', ha='center', va='center', fontsize=10, fontweight='bold', color=BLACK)
    ax.text(10.6, 5.5, 'DeepSeek API', ha='center', va='center', fontsize=FONT_SMALL, color=BLACK)
    ax.text(10.6, 4.6, 'Ollama 本地', ha='center', va='center', fontsize=FONT_SMALL, color='#666666')
    ax.text(10.6, 3.7, 'LangChain', ha='center', va='center', fontsize=FONT_SMALL, color=BLACK)

    # Arrows between layers
    for y1, y2 in [(7.05, 6.75), (5.25, 4.95), (3.45, 3.15)]:
        add_arrow(ax, 6, y1, 6, y2)

    # LLM ↔ business
    add_arrow(ax, 9.5, 6.4, 5.7, 5.6)
    ax.text(7.7, 6.5, 'API调用', ha='center', va='center', fontsize=8, color=BLACK)

    # Side labels
    for y, label in [(7.05, '请求'), (5.25, '调用'), (3.45, 'ORM'), (1.65, 'SQL')]:
        ax.text(0.15, y, label, ha='left', va='center', fontsize=8, color='#666666')

    save_fig(fig, '01_系统架构图')


# ============================================================
# 图2: 功能模块图
# ============================================================
def draw_modules():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_facecolor('white')

    ax.text(7, 8.6, '系统功能模块图', ha='center', va='center', fontsize=FONT_TITLE, fontweight='bold', color=BLACK)

    # Center: diamond
    draw_diamond(ax, 7, 7.0, 5.0, 1.8)
    ax.text(7, 7.0, '国家公园大模型\n智能决策支持系统', ha='center', va='center', fontsize=12, fontweight='bold', color=BLACK)

    modules = [
        (2.3, 4.2, '系统概览\nDashboard', '综合态势感知\n关键指标看板\nGIS地图概览'),
        (5.7, 4.2, '生态监测\nEcology', '多维指标采集\n趋势分析·异常检测\n历史对比分析'),
        (9.1, 4.2, '火灾防控\nFire Control', '火险等级评估\n火势蔓延模拟\n巡护路线优化'),
        (12.5, 4.2, '风险预警\nRisk Warning', '四级预警机制\n蓝·黄·橙·红\n风险联动响应'),
        (4.0, 1.5, '资源调度\nResource', '巡护队统筹管理\n游客流量监控\n资源优化配置'),
        (8.8, 1.5, 'AI 对话\nAI Chat', '大模型智能问答\n多场景专业建议\n上下文感知推荐'),
    ]

    for cx, cy, title, desc in modules:
        draw_box(ax, cx, cy, 3.2, 2.6)
        ax.text(cx, cy + 0.55, title, ha='center', va='center', fontsize=10, fontweight='bold', color=BLACK)
        ax.text(cx, cy - 0.55, desc, ha='center', va='center', fontsize=FONT_SMALL, color=BLACK, linespacing=1.6)

    for cx, cy, _, _ in modules:
        add_line(ax, 7, 6.1, cx, cy + 1.3)

    save_fig(fig, '02_功能模块图')


# ============================================================
# 图3: E-R图
# ============================================================
def draw_er():
    fig, ax = plt.subplots(1, 1, figsize=(16, 9))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_facecolor('white')

    ax.text(7, 8.7, '数据库 E-R 图', ha='center', va='center', fontsize=FONT_TITLE, fontweight='bold', color=BLACK)

    entities = [
        (1.5, 7.0, 'park_zones', 'id (PK) | name | zone_type\nlat | lng | area | boundary\ndescription | core_protection\nrestriction_level'),
        (1.5, 3.0, 'ecological_indicators', 'id (PK) | zone_name (FK)\nvegetation_coverage\nspecies_richness\nwater_quality_index\nsoil_health_index\nair_quality_index\ncarbon_sequestration\nhealth_score'),
        (5.5, 7.0, 'fire_risk_assessments', 'id (PK) | zone_name (FK)\nrisk_level | risk_score\ntemperature | humidity\nwind_speed | wind_direction\nvegetation_type | drought_index\nhistorical_fire_count'),
        (9.5, 7.0, 'risk_alerts', 'id (PK) | zone_name (FK)\nalert_type | alert_level\ntitle | description | lat | lng\nprobability | estimated_impact\nsuggested_actions\nresponse_plan | is_active'),
        (5.0, 3.0, 'resource_schedules', 'id (PK) | zone_name (FK)\npatrol_team | team_size\nzone_name | route_points\nvehicles | equipment\nschedule_date | shift | status'),
        (9.5, 3.0, 'visitor_flows', 'id (PK) | zone_name (FK)\nvisitor_count | capacity\ncongestion_level\nrecorded_at'),
        (13.0, 3.0, 'patrol_logs', 'id (PK) | zone_name (FK)\nteam_name | start_time\nend_time | route_actual\nfindings | status'),
    ]

    for (x, y, name, attrs) in entities:
        lines = attrs.count('\n') + 1
        h = 0.24 * lines + 0.5
        draw_box(ax, x, y - h/2, 3.2, h)
        ax.text(x, y - 0.15, name, ha='center', va='top', fontsize=FONT_BODY, fontweight='bold', color=BLACK)
        ax.text(x, y - 0.35, attrs, ha='center', va='top', fontsize=7.5, color=BLACK, linespacing=1.2)

    # Relationship diamonds and lines
    diamond_positions = [
        (3.5, 7.0, '1:N'),        # park_zones → park_zones
        (7.5, 7.0, '1:N'),        # fire → risk
        (3.2, 4.7, '1:N'),        # park_zones → resource
    ]

    # park_zones → ecological_indicators (vertical)
    draw_diamond(ax, 1.5, 5.2, 0.8, 0.5)
    ax.text(1.5, 5.2, '1:N', ha='center', va='center', fontsize=7, color=BLACK)
    add_line(ax, 1.5, 6.8, 1.5, 5.45)
    add_line(ax, 1.5, 4.95, 1.5, 3.3)

    # park_zones → fire_risk
    draw_diamond(ax, 3.5, 7.0, 0.8, 0.5)
    ax.text(3.5, 7.0, '1:N', ha='center', va='center', fontsize=7, color=BLACK)
    add_line(ax, 3.1, 7.0, 3.1, 7.0)

    # fire → risk_alerts
    draw_diamond(ax, 7.5, 7.0, 0.8, 0.5)
    ax.text(7.5, 7.0, '1:N', ha='center', va='center', fontsize=7, color=BLACK)
    add_line(ax, 7.1, 7.0, 7.1, 7.0)

    # park_zones → resource_schedules
    add_line(ax, 2.8, 6.0, 3.8, 3.5)
    draw_diamond(ax, 3.3, 4.8, 0.8, 0.5)
    ax.text(3.3, 4.8, '1:N', ha='center', va='center', fontsize=7, color=BLACK)
    add_line(ax, 3.3, 4.55, 5.0, 3.3)

    # park_zones → visitor_flows
    add_line(ax, 2.8, 5.7, 7.5, 3.5)

    # park_zones → patrol_logs
    add_line(ax, 3.0, 5.3, 11.5, 3.5)

    save_fig(fig, '03_ER图')


# ============================================================
# 图4: 大模型集成架构图
# ============================================================
def draw_llm():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')
    ax.set_facecolor('white')

    ax.text(6, 6.7, '大模型集成架构图', ha='center', va='center', fontsize=FONT_TITLE, fontweight='bold', color=BLACK)

    # Top: squares
    top_steps = [
        (1.5, 5.0, 2.6, 1.3, '用户输入\n自然语言问题'),
        (4.7, 5.0, 2.6, 1.3, '上下文组装\n生态·火灾·风险·资源数据'),
        (7.9, 5.0, 2.6, 1.3, 'Prompt构建\nSystem Prompt + Context'),
    ]
    for x, y, w, h, text in top_steps:
        draw_box(ax, x, y, w, h)
        ax.text(x, y, text, ha='center', va='center', fontsize=FONT_BODY, color=BLACK)

    add_arrow(ax, 2.8, 5.0, 3.4, 5.0)
    add_arrow(ax, 6.0, 5.0, 6.6, 5.0)

    # LLM Providers: circles
    providers = [
        (3.0, 1.8, 1.1, 'LangChain\n框架', 'LLMService'),
        (6.0, 1.8, 1.1, 'DeepSeek\nAPI', 'deepseek-chat'),
        (9.0, 1.8, 1.1, 'Ollama\n本地', 'Qwen2.5:7b'),
    ]
    for x, y, r, title, sub in providers:
        draw_circle(ax, x, y, r)
        ax.text(x, y + 0.15, title, ha='center', va='center', fontsize=FONT_SMALL, fontweight='bold', color=BLACK)
        ax.text(x, y - 0.35, sub, ha='center', va='center', fontsize=7.5, color='#666666')

    # Arrows from prompt to LLM
    add_arrow(ax, 5.6, 4.3, 3.8, 2.7)
    add_arrow(ax, 6.6, 4.3, 5.4, 2.7)
    add_arrow(ax, 7.6, 4.3, 8.0, 2.7)

    # Lines between LLM providers
    add_line(ax, 4.1, 1.8, 4.9, 1.8)
    add_line(ax, 7.1, 1.8, 7.9, 1.8)

    # Response arrow back
    add_arrow(ax, 4.0, 3.2, 1.5, 4.3)
    ax.text(2.5, 3.7, '响应', ha='center', va='center', fontsize=8, color=BLACK)

    # Fallback box
    ax.text(1.5, 0.6, '服务不可用时\n降级为规则响应', ha='center', va='center', fontsize=7.5, color='#666666')
    draw_box(ax, 1.5, 0.6, 2.8, 0.9)
    add_line(ax, 2.9, 0.6, 3.3, 1.0, style='--')

    save_fig(fig, '04_大模型集成架构图')


# ============================================================
# 图5: 技术架构图
# ============================================================
def draw_tech_stack():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_facecolor('white')

    ax.text(6, 7.7, '系统技术栈架构图', ha='center', va='center', fontsize=FONT_TITLE, fontweight='bold', color=BLACK)

    categories = [
        ('前端技术栈', 2, 5.8, ['Vue 3', 'Vite 6', 'Element Plus', 'ECharts', 'Leaflet', 'Axios', 'Pinia', 'Vue Router']),
        ('后端技术栈', 8.5, 5.5, ['Python 3.12', 'FastAPI', 'Uvicorn', 'SQLAlchemy', 'Pydantic', 'LangChain']),
        ('AI / 大模型', 5.5, 2.5, ['DeepSeek API', 'deepseek-chat', 'LangChain Core', 'LangChain Community', 'Ollama 本地']),
        ('数据存储', 5.5, 0.7, ['SQLite 3', 'Redis (可选)', '文件存储']),
    ]

    for title, cx, cy, items in categories:
        n = len(items)
        cols = min(4, n)
        rows = (n + cols - 1) // cols
        w = cols * 2.3 + 0.5
        h = rows * 0.7 + 0.7

        draw_box(ax, cx, cy, w, h)
        ax.text(cx, cy + h/2 - 0.3, title, ha='center', va='center', fontsize=10, fontweight='bold', color=BLACK)

        for i, item in enumerate(items):
            ix = cx - w/2 + 0.4 + (i % cols) * 2.3
            iy = cy + h/2 - 0.95 - (i // cols) * 0.7
            item_box = FancyBboxPatch((ix, iy - 0.2), 2.1, 0.45, **BOX_KW)
            ax.add_patch(item_box)
            ax.text(ix + 1.05, iy + 0.02, item, ha='center', va='center', fontsize=8, color=BLACK)

    save_fig(fig, '05_技术架构图')


# ============================================================
# 图6: 火灾防控业务流程图
# ============================================================
def draw_fire_flow():
    fig, ax = plt.subplots(1, 1, figsize=(14, 5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 5)
    ax.axis('off')
    ax.set_facecolor('white')

    ax.text(7, 4.7, '火灾防控业务流程', ha='center', va='center', fontsize=FONT_TITLE, fontweight='bold', color=BLACK)

    steps = [
        (1.2, 2.8, '数据采集', '气象传感器\n温湿度·风速\n植被数据'),
        (3.2, 2.8, '风险评估', '多因子火险\n等级计算\n低·中·高·极高'),
        (5.5, 2.8, '预警发布', '四级预警\n蓝→黄→橙→红\n联动通知'),
        (8.0, 2.8, '应急响应', '火势蔓延模拟\n巡护路线优化\n资源调度部署'),
        (10.5, 2.8, '火情处置', '无人机巡查\n灭火资源调配\n实时态势跟踪'),
        (13.0, 2.8, '灾后评估', '过火面积统计\n生态影响评估\n恢复方案制定'),
    ]

    # Data collection: circle
    draw_circle(ax, 1.2, 2.8, 0.9)
    ax.text(1.2, 2.8, '数据采集\n气象·植被', ha='center', va='center', fontsize=7.5, color=BLACK)

    # Risk assessment: diamond (decision)
    draw_diamond(ax, 3.2, 2.8, 1.8, 1.8)
    ax.text(3.2, 2.8, '风险评估\n多因子计算', ha='center', va='center', fontsize=7.5, fontweight='bold', color=BLACK)

    # Alert: square
    draw_box(ax, 5.5, 2.8, 1.8, 2.4)
    ax.text(5.5, 2.8, '预警发布\n四级等级\n蓝→黄→橙→红\n联动通知', ha='center', va='center', fontsize=7.5, color=BLACK)

    # Emergency response: square
    draw_box(ax, 8.0, 2.8, 1.8, 2.4)
    ax.text(8.0, 2.8, '应急响应\n蔓延模拟\n路线优化\n资源部署', ha='center', va='center', fontsize=7.5, color=BLACK)

    # Fire fighting: square
    draw_box(ax, 10.5, 2.8, 1.8, 2.4)
    ax.text(10.5, 2.8, '火情处置\n无人机巡查\n灭火调配\n态势跟踪', ha='center', va='center', fontsize=7.5, color=BLACK)

    # Post assessment: circle (end state)
    draw_circle(ax, 13.0, 2.8, 0.9)
    ax.text(13.0, 2.8, '灾后评估\n恢复方案', ha='center', va='center', fontsize=7.5, color=BLACK)

    # Arrows between steps
    for i in range(len(steps) - 1):
        add_arrow(ax, steps[i][0] + 0.9, 2.8, steps[i + 1][0] - 0.9, 2.8)

    # AI assist label
    ax.text(7, 4.1, 'AI 辅助决策（全程介入）', ha='center', va='center', fontsize=FONT_BODY, fontweight='bold', color=BLACK)

    save_fig(fig, '06_火灾防控业务流程图')


if __name__ == '__main__':
    print("Generating diagrams (academic black-line style with circles/squares/diamonds)...")
    draw_architecture()
    draw_modules()
    draw_er()
    draw_llm()
    draw_tech_stack()
    draw_fire_flow()
    print("\nAll diagrams regenerated in ./diagrams/")
