<template>
  <div class="fire-page">
    <el-row :gutter="16">
      <el-col :span="8" v-for="r in fireRisks" :key="r.id">
        <div class="dashboard-card risk-card" :class="'risk-border-' + r.risk_level">
          <div class="risk-header">
            <span class="risk-zone">{{ r.zone_name }}</span>
            <el-tag :type="riskTagType(r.risk_level)" effect="dark" size="small">{{ riskLabel(r.risk_level) }}</el-tag>
          </div>
          <div class="risk-score">{{ r.risk_score }}</div>
          <div class="risk-factors">
            <div class="factor">
              <span>温度</span><span class="factor-val">{{ r.temperature }}°C</span>
            </div>
            <div class="factor">
              <span>湿度</span><span class="factor-val">{{ r.humidity }}%</span>
            </div>
            <div class="factor">
              <span>风速</span><span class="factor-val">{{ r.wind_speed }} m/s</span>
            </div>
            <div class="factor">
              <span>干旱指数</span><span class="factor-val">{{ r.drought_index }}</span>
            </div>
          </div>
          <div class="risk-meta">
            植被: {{ r.vegetation_type }} | 历史火灾: {{ r.historical_fire_count }}次
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="12">
        <div class="dashboard-card">
          <div class="card-title">
            <el-icon><ScatterPlot /></el-icon> 气象因素与火灾风险相关性
          </div>
          <div ref="scatterChart" style="height:320px"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="dashboard-card">
          <div class="card-title">
            <el-icon><Odometer /></el-icon>
            <span class="card-title-text">火灾蔓延模拟</span>
            <el-button type="warning" size="small" @click="doSimulate">开始模拟</el-button>
          </div>
          <div ref="spreadChart" style="height:320px"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="24">
        <div class="dashboard-card">
          <div class="card-title">
            <el-icon><Guide /></el-icon> 巡护路线优化
            <el-select v-model="routeZone" size="small" style="width:180px;margin-left:12px" placeholder="选择区域">
              <el-option v-for="z in zoneNames" :key="z" :label="z" :value="z" />
            </el-select>
            <el-button type="primary" size="small" style="margin-left:12px" @click="doOptimizeRoutes" :loading="routeLoading">规划路线</el-button>
          </div>
          <div ref="routeMap" style="aspect-ratio:16/8;width:100%;border-radius:8px;margin-top:8px"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { getFireRisks, optimizeRoutes, simulateSpread, getFireCorrelation } from '../api'

const fireRisks = ref([])
const zoneNames = ref([])
const routeZone = ref('')
const routeLoading = ref(false)
const routesResult = ref(null)
const routeMap = ref(null)
const spreadChart = ref(null)
const scatterChart = ref(null)
let routeMapInstance = null
let routeLayerGroup = null

const riskTagType = (lv) => ({ low: 'success', medium: 'warning', high: 'warning', extreme: 'danger' }[lv] || 'info')
const riskLabel = (lv) => ({ low: '低风险', medium: '中风险', high: '高风险', extreme: '极高风险' }[lv] || lv)

onMounted(async () => {
  try {
    const [riskRes, corrRes] = await Promise.all([getFireRisks(), getFireCorrelation()])
    fireRisks.value = riskRes.data || []
    zoneNames.value = fireRisks.value.map(r => r.zone_name)
    initScatterChart(corrRes.data || [])
  } catch {
    useMock()
  }
  initSpreadChart()
  await nextTick()
  initRouteMap()
})

async function doOptimizeRoutes() {
  if (!routeZone.value) return
  routeLoading.value = true
  try {
    const res = await optimizeRoutes(routeZone.value, 2)
    routesResult.value = res.data
    await nextTick()
    drawRoutes()
    if (routeMapInstance) {
      const zone = fireRisks.value.find(r => r.zone_name === routeZone.value)
      if (zone) {
        routeMapInstance.setView([zone.lat, zone.lng], 10, { animate: true })
      }
    }
  } catch {
    routesResult.value = null
  }
  routeLoading.value = false
}

function initRouteMap() {
  if (!routeMap.value) return
  if (routeMapInstance) {
    routeMapInstance.remove()
    routeMapInstance = null
  }
  routeMapInstance = L.map(routeMap.value).setView([33, 104], 5)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap'
  }).addTo(routeMapInstance)

  routeLayerGroup = L.featureGroup().addTo(routeMapInstance)

  const riskColors = { low: '#52c41a', medium: '#faad14', high: '#fa8c16', extreme: '#ff4d4f' }
  fireRisks.value.forEach(r => {
    L.circleMarker([r.lat, r.lng], {
      radius: 10,
      color: riskColors[r.risk_level] || '#1890ff',
      fillColor: riskColors[r.risk_level] || '#1890ff',
      fillOpacity: 0.5,
      weight: 2,
    }).addTo(routeMapInstance)
      .bindPopup(`<b>${r.zone_name}</b><br/>风险等级: ${riskLabel(r.risk_level)}<br/>风险评分: ${r.risk_score}`)
  })

  setTimeout(() => {
    routeMapInstance.invalidateSize()
  }, 200)
}

function drawRoutes() {
  if (!routeLayerGroup || !routeMapInstance) return
  routeLayerGroup.clearLayers()

  const colors = ['#1890ff', '#ff4d4f', '#52c41a']
  const routes = routesResult.value?.routes || []
  routes.forEach((r, i) => {
    if (r.route && r.route.length > 1) {
      const latlngs = r.route.map(p => [p.lat, p.lng])
      L.polyline(latlngs, { color: colors[i % 3], weight: 4, opacity: 0.9 }).addTo(routeLayerGroup)
      latlngs.forEach((ll, j) => {
        L.circleMarker(ll, { radius: 6, color: colors[i % 3], fillOpacity: 0.6 }).addTo(routeLayerGroup)
          .bindPopup(`${r.team} - 第${j + 1}站`)
      })
    }
  })
}

function initScatterChart(data) {
  if (!scatterChart.value) return
  const chart = echarts.init(scatterChart.value)
  const d = data.length ? data : []
  const levelColors = { low: '#52c41a', medium: '#faad14', high: '#fa8c16', extreme: '#ff4d4f' }
  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p) => {
        const point = d[p.dataIndex]
        if (!point) return `${p.name}<br/>温度: ${p.value[0]}°C<br/>风险评分: ${p.value[1]}`
        return `<b>${point.zone_name}</b><br/>温度: ${p.value[0]}°C<br/>风险评分: ${p.value[1]}<br/>等级: ${riskLabel(point.risk_level)}`
      },
    },
    xAxis: { name: '温度(°C)', nameLocation: 'center', nameGap: 30, min: 0, max: 45 },
    yAxis: { name: '风险评分', nameLocation: 'center', nameGap: 35, min: 0, max: 100 },
    series: [{
      type: 'scatter',
      data: d.map(r => ({
        value: [r.temperature, r.risk_score],
        itemStyle: { color: levelColors[r.risk_level] || '#1890ff' },
        symbolSize: 18,
      })),
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.5)' } },
    }],
    grid: { left: 50, right: 30, top: 20, bottom: 40 },
  })
}

async function doSimulate() {
  const zone = fireRisks.value[0] || { lat: 33.1, lng: 104.0 }
  try {
    const res = await simulateSpread(zone.lat || 33.1, zone.lng || 104.0, 6)
    initSpreadChart(res.data?.prediction)
  } catch {
    initSpreadChart()
  }
}

function initSpreadChart(prediction) {
  if (!spreadChart.value) return
  const chart = echarts.init(spreadChart.value)
  let data = prediction
  if (!data) {
    data = []
    for (let h = 1; h <= 6; h++) {
      data.push({ hour: h, radius_km: +(h * 1.2 + Math.random() * 0.5).toFixed(2), affected_area_km2: +(Math.PI * (h * 1.2) ** 2).toFixed(2) })
    }
  }
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { top: 0, itemWidth: 14, itemHeight: 14, textStyle: { fontSize: 12 } },
    xAxis: { type: 'category', data: data.map(d => `${d.hour}h`), name: '时间' },
    yAxis: [
      { type: 'value', name: '蔓延半径(km)' },
      { type: 'value', name: '受影响面积(km²)' },
    ],
    series: [
      { name: '蔓延半径', type: 'bar', data: data.map(d => d.radius_km), color: '#ff7875' },
      { name: '受影响面积', type: 'line', yAxisIndex: 1, data: data.map(d => d.affected_area_km2), color: '#ff4d4f' },
    ],
    grid: { left: 50, right: 50, top: 40, bottom: 30 },
  })
}

function useMock() {
  fireRisks.value = [
    { id: 1, zone_name: '大熊猫栖息地', lat: 33.1, lng: 104.0, risk_level: 'high', risk_score: 68.5,
      temperature: 34.2, humidity: 25.3, wind_speed: 15.2, wind_direction: 'SW', vegetation_type: '阔叶林',
      drought_index: 72.1, historical_fire_count: 3 },
    { id: 2, zone_name: '祁连山草甸区', lat: 38.3, lng: 99.5, risk_level: 'extreme', risk_score: 82.3,
      temperature: 36.8, humidity: 18.5, wind_speed: 22.1, wind_direction: 'NW', vegetation_type: '草原',
      drought_index: 88.2, historical_fire_count: 5 },
    { id: 3, zone_name: '三江源核心区', lat: 34.2, lng: 92.5, risk_level: 'medium', risk_score: 42.1,
      temperature: 22.5, humidity: 55.3, wind_speed: 8.6, wind_direction: 'E', vegetation_type: '高山草甸',
      drought_index: 35.2, historical_fire_count: 0 },
    { id: 4, zone_name: '海南热带雨林', lat: 19.0, lng: 109.5, risk_level: 'low', risk_score: 18.7,
      temperature: 28.1, humidity: 78.2, wind_speed: 5.2, wind_direction: 'SE', vegetation_type: '阔叶林',
      drought_index: 15.3, historical_fire_count: 1 },
  ]
  zoneNames.value = fireRisks.value.map(r => r.zone_name)

  initScatterChart(fireRisks.value.map(r => ({
    zone_name: r.zone_name,
    temperature: r.temperature,
    risk_score: r.risk_score,
    risk_level: r.risk_level,
  })))
}
</script>

<style scoped>
.risk-card { position: relative; overflow: hidden; }
.risk-border-low { border-left: 4px solid #52c41a; }
.risk-border-medium { border-left: 4px solid #faad14; }
.risk-border-high { border-left: 4px solid #fa8c16; }
.risk-border-extreme { border-left: 4px solid #ff4d4f; }
.risk-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.risk-zone { font-weight: 600; font-size: 16px; }
.risk-score { font-size: 42px; font-weight: 700; color: #ff4d4f; line-height: 1.2; }
.risk-border-low .risk-score { color: #52c41a; }
.risk-border-medium .risk-score { color: #faad14; }
.risk-factors { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 16px; margin: 8px 0; }
.factor { display: flex; justify-content: space-between; font-size: 13px; color: #666; }
.factor-val { font-weight: 600; }
.risk-meta { font-size: 12px; color: #999; margin-top: 8px; padding-top: 8px; border-top: 1px solid #f0f0f0; }
.card-title-text { white-space: nowrap; }
</style>
