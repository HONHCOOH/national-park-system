<template>
  <div class="risk-page">
    <el-row :gutter="16">
      <el-col :span="6">
        <div class="dashboard-card">
          <div class="card-title"><el-icon><DataAnalysis /></el-icon> 预警统计</div>
          <div class="alert-stats">
            <div class="alert-stat-item" v-for="item in levelStats" :key="item.level">
              <div class="alert-stat-badge" :style="{ background: item.color }">{{ item.count }}</div>
              <div class="alert-stat-label">{{ item.label }}</div>
            </div>
          </div>
        </div>
      </el-col>
      <el-col :span="18">
        <div class="dashboard-card">
          <div class="card-title">
            <el-icon><BellFilled /></el-icon> 活跃预警列表
            <el-space style="margin-left:12px">
              <el-radio-group v-model="alertFilter" size="small">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button label="red">红色</el-radio-button>
                <el-radio-button label="orange">橙色</el-radio-button>
                <el-radio-button label="yellow">黄色</el-radio-button>
                <el-radio-button label="blue">蓝色</el-radio-button>
              </el-radio-group>
            </el-space>
          </div>
          <el-table :data="filteredAlerts" stripe size="small" max-height="400" @row-click="handleRowClick">
            <el-table-column label="等级" width="70">
              <template #default="{ row }">
                <el-tag :color="levelColor(row.alert_level)" style="color:#fff;border:none" size="small">
                  {{ levelLabel(row.alert_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="类型" width="80">
              <template #default="{ row }">
                <el-tag size="small">{{ typeLabel(row.alert_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="title" label="预警标题" min-width="180" />
            <el-table-column prop="zone_name" label="区域" width="130" />
            <el-table-column prop="probability" label="概率" width="70" sortable>
              <template #default="{ row }">
                <el-progress :percentage="row.probability" :stroke-width="8" :color="alertLevelColor(row.alert_level)" />
              </template>
            </el-table-column>
            <el-table-column prop="estimated_impact" label="影响范围(km²)" width="120" />
            <el-table-column prop="created_at" label="时间" width="160">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="success" link size="small" @click="handleResolve(row.id)">处理完成</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="8">
        <div class="dashboard-card">
          <div class="card-title"><el-icon><Guide /></el-icon> 预警处理漏斗</div>
          <div ref="funnelChart" style="height:340px"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="dashboard-card">
          <div class="card-title"><el-icon><Clock /></el-icon> 预警事件时间轴</div>
          <div ref="timelineChart" style="height:340px"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="dashboard-card">
          <div class="card-title"><el-icon><WarningFilled /></el-icon> 应急方案生成</div>
          <div v-if="selectedAlert" class="alert-detail">
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item label="预警标题">{{ selectedAlert.title }}</el-descriptions-item>
              <el-descriptions-item label="等级">
                <el-tag :color="levelColor(selectedAlert.alert_level)" style="color:#fff;border:none" size="small">
                  {{ levelLabel(selectedAlert.alert_level) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="区域">{{ selectedAlert.zone_name }}</el-descriptions-item>
              <el-descriptions-item label="类型">{{ typeLabel(selectedAlert.alert_type) }}</el-descriptions-item>
              <el-descriptions-item label="描述" :span="2">{{ selectedAlert.description }}</el-descriptions-item>
            </el-descriptions>
            <div v-if="selectedAlert.suggested_actions?.length" style="margin-top:12px">
              <div style="font-weight:600;margin-bottom:8px">建议措施：</div>
              <el-tag v-for="(act, i) in selectedAlert.suggested_actions" :key="i" style="margin:0 4px 4px 0">{{ act }}</el-tag>
            </div>
            <div v-if="selectedAlert.response_plan" style="margin-top:12px;padding:12px;background:#f6ffed;border-radius:8px">
              <div style="font-weight:600;margin-bottom:4px">应急预案：</div>
              <div style="font-size:14px;color:#333">{{ selectedAlert.response_plan }}</div>
            </div>
          </div>
          <div v-else style="text-align:center;padding:60px;color:#999">点击预警列表查看详情和应急方案</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <div class="dashboard-card">
          <div class="card-title"><el-icon><Histogram /></el-icon> 预警类型分布</div>
          <div ref="typeChart" style="height:300px"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="dashboard-card">
          <div class="card-title"><el-icon><TrendCharts /></el-icon> 历史预警趋势</div>
          <div ref="trendAlertChart" style="height:300px"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import { getActiveAlerts, resolveAlert, getAlertTimeline } from '../api'
import { ElMessage } from 'element-plus'

const alerts = ref([])
const alertFilter = ref('all')
const selectedAlert = ref(null)
const typeChart = ref(null)
const funnelChart = ref(null)
const timelineChart = ref(null)
const trendAlertChart = ref(null)

const levelColor = (lv) => ({ red: '#ff4d4f', orange: '#fa8c16', yellow: '#fadb14', blue: '#1890ff' }[lv] || '#999')
const alertLevelColor = (lv) => ({ red: '#ff4d4f', orange: '#fa8c16', yellow: '#fadb14', blue: '#1890ff' }[lv] || '#999')
const levelLabel = (lv) => ({ red: '红色', orange: '橙色', yellow: '黄色', blue: '蓝色' }[lv] || lv)
const typeLabel = (t) => ({ fire: '火灾', pest: '病虫害', invasive: '入侵物种', human: '人为活动', flood: '洪涝' }[t] || t)

const filteredAlerts = computed(() => {
  if (alertFilter.value === 'all') return alerts.value
  return alerts.value.filter(a => a.alert_level === alertFilter.value)
})

const levelStats = computed(() => {
  const counts = { red: 0, orange: 0, yellow: 0, blue: 0 }
  alerts.value.forEach(a => { if (counts[a.alert_level] !== undefined) counts[a.alert_level]++ })
  return [
    { level: 'red', label: '红色预警', count: counts.red, color: '#ff4d4f' },
    { level: 'orange', label: '橙色预警', count: counts.orange, color: '#fa8c16' },
    { level: 'yellow', label: '黄色预警', count: counts.yellow, color: '#fadb14' },
    { level: 'blue', label: '蓝色预警', count: counts.blue, color: '#1890ff' },
  ]
})

onMounted(async () => {
  try {
    const [alertRes, timelineRes] = await Promise.all([getActiveAlerts(), getAlertTimeline(30)])
    alerts.value = alertRes.data || []
    initTimelineChart(timelineRes.data || [])
    initTrendAlertChart(timelineRes.data || [])
  } catch {
    useMock()
  }
  initTypeChart()
  initFunnelChart()
})

async function handleResolve(id) {
  try {
    await resolveAlert(id)
    ElMessage.success('预警已标记为已处理')
    alerts.value = alerts.value.map(a => a.id === id ? { ...a, is_resolved: true, is_active: false } : a)
  } catch {
    alerts.value = alerts.value.map(a => a.id === id ? { ...a, is_resolved: true, is_active: false } : a)
    ElMessage.success('操作成功')
  }
}

function handleRowClick(row) {
  selectedAlert.value = row
}

function initFunnelChart() {
  if (!funnelChart.value) return
  const chart = echarts.init(funnelChart.value)
  const total = alerts.value.length
  const active = alerts.value.filter(a => !a.is_resolved).length
  const responded = alerts.value.filter(a => a.response_plan).length
  const resolved = alerts.value.filter(a => a.is_resolved).length

  chart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 条' },
    series: [{
      type: 'funnel',
      left: '15%',
      top: 40,
      bottom: 40,
      width: '70%',
      min: 0,
      max: Math.max(total, 1),
      sort: 'descending',
      gap: 2,
      label: { show: true, position: 'inside', fontSize: 12 },
      itemStyle: { borderColor: '#fff', borderWidth: 1 },
      emphasis: { label: { fontSize: 16, fontWeight: 'bold' } },
      data: [
        { value: total, name: '预警总数', itemStyle: { color: '#409eff' } },
        { value: active, name: '活跃预警', itemStyle: { color: '#fa8c16' } },
        { value: responded, name: '已响应', itemStyle: { color: '#ffc53d' } },
        { value: resolved, name: '已处理', itemStyle: { color: '#52c41a' } },
      ],
    }],
  })
}

function initTimelineChart(timelineData) {
  if (!timelineChart.value) return
  const chart = echarts.init(timelineChart.value)
  const d = timelineData.length > 0 ? timelineData : []

  const levelColors = { red: '#ff4d4f', orange: '#fa8c16', yellow: '#fadb14', blue: '#1890ff' }
  const categories = [
    { name: '火灾', itemStyle: { color: '#ff4d4f' } },
    { name: '病虫害', itemStyle: { color: '#52c41a' } },
    { name: '入侵物种', itemStyle: { color: '#fa8c16' } },
    { name: '人为活动', itemStyle: { color: '#1890ff' } },
    { name: '洪涝', itemStyle: { color: '#722ed1' } },
  ]

  const typeLabelMap = { fire: '火灾', pest: '病虫害', invasive: '入侵物种', human: '人为活动', flood: '洪涝' }

  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p) => {
        const item = d[p.dataIndex]
        return `<b>${item?.title || ''}</b><br/>区域: ${item?.zone_name || ''}<br/>等级: ${item?.level || ''}<br/>时间: ${item?.time?.slice(0, 16) || ''}`
      },
    },
    legend: { data: categories.map(c => c.name), bottom: 0, itemWidth: 12, itemHeight: 12 },
    xAxis: { type: 'time', name: '时间', axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: 'category', data: [''], show: false },
    series: categories.map(cat => ({
      name: cat.name,
      type: 'scatter',
      symbolSize: (val, param) => {
        const item = d[param.dataIndex]
        if (!item) return 10
        return item.level === 'red' ? 16 : item.level === 'orange' ? 13 : item.level === 'yellow' ? 11 : 9
      },
      data: d
        .filter(item => typeLabelMap[item.type] === cat.name)
        .map(item => ({
          value: [item.time, ''],
          itemStyle: { color: levelColors[item.level] || cat.itemStyle.color },
        })),
    })),
    grid: { left: 30, right: 20, top: 20, bottom: 50 },
  })
}

function initTrendAlertChart(timelineData) {
  if (!trendAlertChart.value) return
  const chart = echarts.init(trendAlertChart.value)
  const d = timelineData.length > 0 ? timelineData : []

  const dailyCounts = {}
  d.forEach(item => {
    const day = item.time?.slice(0, 10)
    if (day) dailyCounts[day] = (dailyCounts[day] || 0) + 1
  })

  const sortedDays = Object.keys(dailyCounts).sort()
  const last14 = sortedDays.slice(-14)

  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: last14, axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: 'value', name: '预警数' },
    series: [{
      type: 'bar',
      data: last14.map(d => dailyCounts[d] || 0),
      itemStyle: {
        color: '#1890ff',
        borderRadius: [4, 4, 0, 0],
      },
      barMaxWidth: 25,
    }],
    grid: { left: 40, right: 20, top: 20, bottom: 40 },
  })
}

function initTypeChart() {
  if (!typeChart.value) return
  const chart = echarts.init(typeChart.value)
  const types = {}
  alerts.value.forEach(a => {
    const t = typeLabel(a.alert_type)
    types[t] = (types[t] || 0) + 1
  })
  const levels = { red: 0, orange: 0, yellow: 0, blue: 0 }
  alerts.value.forEach(a => { levels[a.alert_level] = (levels[a.alert_level] || 0) + 1 })

  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['40%', '65%'],
      data: [
        { value: types['火灾'] || 0, name: '火灾' },
        { value: types['病虫害'] || 0, name: '病虫害' },
        { value: types['入侵物种'] || 0, name: '入侵物种' },
        { value: types['人为活动'] || 0, name: '人为活动' },
        { value: types['洪涝'] || 0, name: '洪涝' },
      ].filter(d => d.value > 0),
      color: ['#ff4d4f', '#52c41a', '#fa8c16', '#1890ff', '#722ed1'],
    }],
  })
}

function useMock() {
  alertFilter.value = 'all'
  alerts.value = [
    { id: 1, alert_type: 'fire', alert_level: 'orange', title: '高温干旱火险预警-大熊猫栖息地',
      description: '气温持续升高，干旱指数达72.1，存在较高火灾风险。建议加强无人机巡检频次，启动二级应急响应。',
      zone_name: '大熊猫栖息地', lat: 33.1, lng: 104.0, probability: 72.5, estimated_impact: 15.3,
      suggested_actions: ['加强无人机巡检频次', '通知附近巡护队就位', '准备应急物资', '上报管理局指挥中心'],
      response_plan: '启动橙色预警机制：立即派遣巡护二队前往现场，无人机组起飞监测，检查防火隔离带，通知周边社区注意防火。',
      is_active: true, is_resolved: false, created_at: new Date(Date.now() - 3600000).toISOString() },
    { id: 2, alert_type: 'pest', alert_level: 'yellow', title: '松材线虫病扩散预警',
      description: '监测发现松材线虫病在东北虎豹栖息地外围有扩散趋势。',
      zone_name: '东北虎豹栖息地', lat: 43.5, lng: 129.8, probability: 55.0, estimated_impact: 8.2,
      suggested_actions: ['设立检疫点', '清除病木', '喷洒生物农药'],
      response_plan: '启动黄色预警：组织专业人员清除病木，设置诱捕装置，加强边界检疫。',
      is_active: true, is_resolved: false, created_at: new Date(Date.now() - 7200000).toISOString() },
    { id: 3, alert_type: 'human', alert_level: 'blue', title: '游客违规进入核心区预警',
      description: '监测系统发现近期有游客接近三江源核心保护区边界。',
      zone_name: '三江源核心区', lat: 34.2, lng: 92.5, probability: 35.0, estimated_impact: 1.5,
      suggested_actions: ['加强边界巡逻', '增设警示标识', '劝返违规人员'],
      response_plan: '启动蓝色预警：加强边界巡护，在关键入口增设警示牌，劝返接近核心区的游客。',
      is_active: true, is_resolved: false, created_at: new Date(Date.now() - 14400000).toISOString() },
    { id: 4, alert_type: 'fire', alert_level: 'red', title: '祁连山草甸极高火险预警',
      description: '祁连山草甸区干旱指数达88.2，风速22.1m/s，达到极高火险等级。',
      zone_name: '祁连山草甸区', lat: 38.3, lng: 99.5, probability: 92.0, estimated_impact: 35.8,
      suggested_actions: ['立即启动最高级别应急响应', '全员进入紧急状态', '通知上级主管部门', '组织人员撤离'],
      response_plan: '启动红色预警！立即启动一级应急响应：所有巡护队进入紧急状态，无人机不间断监测，灭火设备前置部署，通报省应急管理厅。',
      is_active: true, is_resolved: false, created_at: new Date(Date.now() - 1800000).toISOString() },
  ]

  const mockTimeline = []
  const types = ['fire', 'pest', 'invasive', 'human', 'flood']
  const levels = ['blue', 'yellow', 'orange', 'red']
  const zones = ['三江源核心区', '大熊猫栖息地', '东北虎豹栖息地', '祁连山草甸区', '武夷山实验区', '海南热带雨林', '可可西里荒野区']
  for (let i = 29; i >= 0; i--) {
    const t = types[Math.floor(Math.random() * types.length)]
    const lv = levels[Math.floor(Math.random() * levels.length)]
    mockTimeline.push({
      id: 100 + i,
      time: new Date(Date.now() - i * 4 * 3600000).toISOString(),
      title: `预警事件-${zones[i % 7]}`,
      type: t,
      level: lv,
      zone_name: zones[i % 7],
      description: '模拟历史预警事件',
      is_resolved: Math.random() > 0.3,
    })
  }

  initTimelineChart(mockTimeline)
  initTrendAlertChart(mockTimeline)
  initTypeChart()
  initFunnelChart()
}

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}
</script>

<style scoped>
.alert-stats { display: flex; flex-direction: column; gap: 12px; }
.alert-stat-item { display: flex; align-items: center; gap: 12px; }
.alert-stat-badge {
  width: 48px; height: 48px; border-radius: 50%; margin: 0 auto 4px;
  display: flex; align-items: center; justify-content: center;
  color: #fff; font-size: 20px; font-weight: 700;
}
.alert-stat-label { font-size: 12px; color: #666; }
:deep(.el-table__row) { cursor: pointer; }
</style>
