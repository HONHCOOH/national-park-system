<template>
  <div class="dashboard">
    <el-row :gutter="16" class="stats-row">
      <el-col :span="6" v-for="stat in statsCards" :key="stat.label">
        <div class="dashboard-card stat-card">
          <div class="stat-icon" :style="{ background: stat.color }">
            <el-icon :size="24"><component :is="stat.icon" /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
          <el-tag v-if="stat.trend" :type="stat.trendType" size="small">{{ stat.trend }}</el-tag>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="6">
        <div class="dashboard-card">
          <div class="card-title">
            <el-icon><Odometer /></el-icon> 综合健康评分
          </div>
          <div ref="gaugeChart" style="height: 240px"></div>
        </div>
      </el-col>
      <el-col :span="9">
        <div class="dashboard-card">
          <div class="card-title">
            <el-icon><TrendCharts /></el-icon> 生态健康趋势 (近7天)
          </div>
          <div ref="trendChart" style="height: 240px"></div>
        </div>
      </el-col>
      <el-col :span="9">
        <div class="dashboard-card">
          <div class="card-title">
            <el-icon><BellFilled /></el-icon> 活跃预警分布
          </div>
          <div ref="alertChart" style="height: 240px"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="14">
        <div class="dashboard-card">
          <div class="card-title">
            <el-icon><MapLocation /></el-icon> 园区区域概览
            <el-switch v-model="showHeatmap" active-text="热力图" inactive-text="标记" size="small" style="margin-left:12px" @change="toggleHeatmap" />
          </div>
          <div ref="mapContainer" style="height: 380px; border-radius: 8px;"></div>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="dashboard-card">
          <div class="card-title">
            <el-icon><Histogram /></el-icon> 各区域健康评分
          </div>
          <div ref="zoneBarChart" style="height: 380px"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { getStats, getZones, getFireHeatmap } from '../api'

const stats = ref({ avg_health_score: 0, total_zones: 0, active_alerts: 0, patrol_teams: 0, today_anomalies: 0, eco_health_trend: [], alert_distribution: { by_level: {}, by_type: {} } })
const zones = ref([])
const trendChart = ref(null)
const alertChart = ref(null)
const gaugeChart = ref(null)
const zoneBarChart = ref(null)
const mapContainer = ref(null)
const showHeatmap = ref(false)
let map = null
let heatmapLayer = null
let heatmapGroup = null

const statsCards = ref([
  { label: '生态健康评分', value: '--', icon: 'Sunny', color: '#e6f7ff', trend: '', trendType: 'success' },
  { label: '园区区域数', value: '--', icon: 'OfficeBuilding', color: '#f6ffed', trend: '', trendType: 'success' },
  { label: '活跃预警数', value: '--', icon: 'BellFilled', color: '#fff7e6', trend: '', trendType: 'warning' },
  { label: '在岗巡护队', value: '--', icon: 'UserFilled', color: '#f0f5ff', trend: '', trendType: 'info' },
])

onMounted(async () => {
  try {
    const [sRes, zRes, hRes] = await Promise.all([getStats(), getZones(), getFireHeatmap()])
    const s = sRes.data
    stats.value = s
    zones.value = zRes.data

    statsCards.value[0].value = s.avg_health_score
    statsCards.value[1].value = s.total_zones
    statsCards.value[2].value = s.active_alerts
    statsCards.value[3].value = s.patrol_teams
    statsCards.value[0].trend = s.avg_health_score > 75 ? '健康' : '注意'
    statsCards.value[2].trend = s.active_alerts > 5 ? '需关注' : '正常'
    statsCards.value[2].trendType = s.active_alerts > 5 ? 'warning' : 'success'

    initGaugeChart(s.avg_health_score || 0)
    initTrendChart(s.eco_health_trend || [])
    initAlertChart(s.alert_distribution || { by_level: {}, by_type: {} })
    initZoneBarChart(zRes.data || [])
    initMap(zRes.data || [])
    heatmapPoints.value = hRes.data || []
  } catch (e) {
    console.warn('API未连接，使用模拟数据', e)
    useMockData()
  }
})

const heatmapPoints = ref([])

function useMockData() {
  statsCards.value[0].value = '78.5'
  statsCards.value[1].value = '8'
  statsCards.value[2].value = '3'
  statsCards.value[3].value = '8'
  statsCards.value[2].trend = '正常'
  statsCards.value[2].trendType = 'success'

  initGaugeChart(78.5)

  const mockTrend = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(Date.now() - i * 86400000)
    mockTrend.push({ date: `${d.getMonth()+1}-${d.getDate()}`, avg_health: Math.round((75 + Math.random() * 10) * 10) / 10 })
  }
  initTrendChart(mockTrend)
  initAlertChart({ by_level: { red: 1, orange: 2, yellow: 3, blue: 5 }, by_type: { fire: 4, pest: 3, human: 2, invasive: 1, flood: 1 } })

  const mockZones = [
    { name: '三江源核心区', lat: 34.2, lng: 92.5, zone_type: '湿地', health_score: 82 },
    { name: '大熊猫栖息地', lat: 33.1, lng: 104.0, zone_type: '森林', health_score: 88 },
    { name: '东北虎豹栖息地', lat: 43.5, lng: 129.8, zone_type: '森林', health_score: 76 },
    { name: '祁连山草甸区', lat: 38.3, lng: 99.5, zone_type: '草原', health_score: 71 },
    { name: '武夷山实验区', lat: 27.6, lng: 117.8, zone_type: '森林', health_score: 85 },
    { name: '海南热带雨林', lat: 19.0, lng: 109.5, zone_type: '森林', health_score: 90 },
    { name: '普达措湿地区', lat: 27.8, lng: 99.9, zone_type: '湿地', health_score: 79 },
    { name: '可可西里荒野区', lat: 35.5, lng: 90.0, zone_type: '高山', health_score: 74 },
  ]
  initZoneBarChart(mockZones)
  initMap(mockZones)

  heatmapPoints.value = []
  for (let i = 0; i < 80; i++) {
    const z = mockZones[Math.floor(Math.random() * mockZones.length)]
    heatmapPoints.value.push({
      lat: z.lat + (Math.random() - 0.5) * 1.5,
      lng: z.lng + (Math.random() - 0.5) * 1.5,
      value: Math.random() * 100,
      zone_name: z.name,
    })
  }
}

function initGaugeChart(score) {
  if (!gaugeChart.value) return
  const chart = echarts.init(gaugeChart.value)
  chart.setOption({
    series: [{
      type: 'gauge',
      startAngle: 210,
      endAngle: -30,
      center: ['50%', '55%'],
      radius: '85%',
      min: 0,
      max: 100,
      splitNumber: 10,
      axisLine: {
        show: true,
        lineStyle: {
          width: 18,
          color: [
            [0.3, '#ff4d4f'],
            [0.6, '#faad14'],
            [0.8, '#52c41a'],
            [1, '#1890ff'],
          ],
        },
      },
      pointer: {
        icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
        length: '70%',
        width: 6,
        offsetCenter: [0, '-10%'],
        itemStyle: { color: 'auto' },
      },
      axisTick: { distance: -18, length: 8, lineStyle: { width: 1, color: '#999' } },
      splitLine: { distance: -22, length: 18, lineStyle: { width: 2, color: '#999' } },
      axisLabel: { color: '#999', distance: 30, fontSize: 9 },
      detail: {
        valueAnimation: true,
        fontSize: 28,
        fontWeight: '700',
        offsetCenter: [0, '50%'],
        formatter: '{value}',
        color: score > 80 ? '#52c41a' : score > 60 ? '#faad14' : '#ff4d4f',
      },
      title: { offsetCenter: [0, '78%'], fontSize: 12, color: '#666' },
      data: [{ value: score, name: '综合健康评分' }],
    }],
  })
  setTimeout(() => chart.resize(), 100)
}

function initZoneBarChart(zoneList) {
  if (!zoneBarChart.value || !zoneList.length) return
  const chart = echarts.init(zoneBarChart.value)
  const sorted = [...zoneList].sort((a, b) => (b.health_score || 0) - (a.health_score || 0))
  chart.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'category',
      data: sorted.map(z => z.name),
      axisLabel: { rotate: 30, fontSize: 10 },
    },
    yAxis: { type: 'value', min: 50, max: 100, name: '评分' },
    series: [{
      type: 'bar',
      data: sorted.map(z => ({
        value: z.health_score || 0,
        itemStyle: {
          color: (z.health_score || 0) > 80 ? '#52c41a' : (z.health_score || 0) > 70 ? '#faad14' : '#ff4d4f',
          borderRadius: [4, 4, 0, 0],
        },
      })),
      barMaxWidth: 30,
      label: { show: true, position: 'top', fontSize: 11, fontWeight: 600 },
    }],
    grid: { left: 40, right: 20, top: 20, bottom: 70 },
  })
}

function toggleHeatmap(val) {
  if (!map) return
  if (val) {
    loadHeatmap()
  } else {
    if (heatmapLayer) {
      map.removeLayer(heatmapLayer)
      heatmapLayer = null
    }
  }
}

function loadHeatmap() {
  if (!map || !heatmapPoints.value.length) return
  if (heatmapLayer) map.removeLayer(heatmapLayer)
  heatmapLayer = L.layerGroup()
  const getColor = (v) => {
    if (v > 80) return '#ff4d4f'
    if (v > 60) return '#fa8c16'
    if (v > 40) return '#faad14'
    if (v > 20) return '#52c41a'
    return '#1890ff'
  }
  heatmapPoints.value.forEach(p => {
    const r = 8 + (p.value / 100) * 20
    L.circle([p.lat, p.lng], {
      radius: r * 1000,
      color: getColor(p.value),
      fillColor: getColor(p.value),
      fillOpacity: 0.3,
      weight: 0,
    }).addTo(heatmapLayer)
  })
  heatmapLayer.addTo(map)
}

function initTrendChart(data) {
  if (!trendChart.value) return
  const chart = echarts.init(trendChart.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data.map(d => d.date) },
    yAxis: { type: 'value', min: 50, max: 100, axisLabel: { formatter: '{value}' } },
    series: [{
      data: data.map(d => d.avg_health),
      type: 'line',
      smooth: true,
      lineStyle: { color: '#1890ff', width: 3 },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: 'rgba(24,144,255,0.3)' },
        { offset: 1, color: 'rgba(24,144,255,0.05)' }
      ])},
      itemStyle: { color: '#1890ff' },
    }],
    grid: { left: 40, right: 20, top: 10, bottom: 30 },
  })
}

function initAlertChart(dist) {
  if (!alertChart.value) return
  const chart = echarts.init(alertChart.value)
  const levels = dist.by_level || {}
  chart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      avoidLabelOverlap: false,
      label: { show: true, formatter: '{b}\n{d}%' },
      data: [
        { value: levels.red || 0, name: '红色预警' },
        { value: levels.orange || 0, name: '橙色预警' },
        { value: levels.yellow || 0, name: '黄色预警' },
        { value: levels.blue || 0, name: '蓝色预警' },
      ],
      color: ['#ff4d4f', '#fa8c16', '#fadb14', '#1890ff'],
    }],
  })
}

function initMap(zoneList) {
  if (!mapContainer.value || map) return
  map = L.map(mapContainer.value).setView([33, 102], 5)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap'
  }).addTo(map)

  zoneList.forEach(z => {
    const color = (z.health_score || 70) > 80 ? '#52c41a' : (z.health_score || 70) > 70 ? '#faad14' : '#ff4d4f'
    const marker = L.circleMarker([z.lat, z.lng], {
      radius: 10,
      fillColor: color,
      color: '#fff',
      weight: 2,
      fillOpacity: 0.8,
    }).addTo(map)
    marker.bindPopup(`<b>${z.name}</b><br/>类型: ${z.zone_type}<br/>健康评分: ${z.health_score || '--'}`)
  })
}
</script>

<style scoped>
.stats-row { margin-bottom: 0; }
.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.stat-info { flex: 1; }
.stat-value { font-size: 32px; font-weight: 700; color: #1a1a1a; line-height: 1.2; }
.stat-label { font-size: 13px; color: #999; }
.stat-card > .el-tag { position: absolute; top: 12px; right: 12px; }
</style>
