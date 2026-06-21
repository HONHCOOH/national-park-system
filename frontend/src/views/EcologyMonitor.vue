<template>
  <div class="ecology-page">
    <el-row :gutter="16">
      <el-col :span="14">
        <div class="dashboard-card">
          <div class="card-title">
            <el-icon><Sunny /></el-icon> 实时生态指标
            <el-select v-model="selectedZone" placeholder="所有区域" clearable style="width:180px;margin-left:12px" size="small">
              <el-option v-for="z in zoneOptions" :key="z" :label="z" :value="z" />
            </el-select>
          </div>
          <el-table :data="indicators" stripe size="small" max-height="350">
            <el-table-column prop="zone_name" label="区域" width="140" />
            <el-table-column prop="ecological_health_score" label="健康评分" width="90" sortable>
              <template #default="{ row }">
                <el-tag :type="row.ecological_health_score > 80 ? 'success' : row.ecological_health_score > 60 ? 'warning' : 'danger'" size="small">
                  {{ row.ecological_health_score }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="vegetation_coverage" label="植被覆盖" width="90" />
            <el-table-column prop="species_richness" label="物种数" width="80" />
            <el-table-column prop="species_diversity_index" label="多样性" width="80" />
            <el-table-column prop="water_quality_index" label="水质指数" width="90" />
            <el-table-column prop="soil_health_index" label="土壤健康" width="90" />
            <el-table-column prop="air_quality_index" label="空气质量" width="90" />
            <el-table-column prop="anomaly_flag" label="异常" width="70">
              <template #default="{ row }">
                <el-tag v-if="row.anomaly_flag" type="danger" size="small">异常</el-tag>
                <el-tag v-else type="success" size="small">正常</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="recorded_at" label="记录时间" width="160">
              <template #default="{ row }">{{ formatTime(row.recorded_at) }}</template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="dashboard-card anomaly-card">
          <div class="card-title"><el-icon><WarningFilled /></el-icon> 生态异常</div>
          <div v-if="anomalies.length === 0" style="color:#999;text-align:center;padding:20px">暂无异常</div>
          <div v-for="a in anomalies" :key="a.id" class="anomaly-item">
            <el-tag type="danger" size="small">异常</el-tag>
            <span style="font-weight:600">{{ a.zone_name }}</span>
            <span style="color:#999;font-size:12px">{{ a.recorded_at?.slice(0,16) }}</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="15">
        <div class="dashboard-card">
          <div class="card-title">
            <el-icon><DataAnalysis /></el-icon> 多维度生态指标雷达对比
            <span style="font-size:12px;color:#999;margin-left:8px">（各园区六维生态指标对比）</span>
          </div>
          <div ref="radarChart" style="height:420px"></div>
        </div>
      </el-col>
      <el-col :span="9">
        <div class="dashboard-card trend-card">
          <div class="card-title"><el-icon><TrendCharts /></el-icon> 健康趋势</div>
          <div ref="healthChart" style="height:420px"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { getEcologyIndicators, getEcologyHistory, getAnomalies, getRadarData } from '../api'
import { ElMessage } from 'element-plus'

const selectedZone = ref('')
const zoneOptions = ref([])
const indicators = ref([])
const anomalies = ref([])
const healthChart = ref(null)
const radarChart = ref(null)

onMounted(async () => {
  try {
    const [indRes, anoRes, radarRes] = await Promise.all([
      getEcologyIndicators(),
      getAnomalies(10),
      getRadarData(),
    ])
    indicators.value = indRes.data || []
    anomalies.value = anoRes.data || []
    zoneOptions.value = [...new Set(indicators.value.map(i => i.zone_name))]
    initHealthChart()
    initRadarChart(radarRes.data || { indicators: [], series: [] })
  } catch (e) {
    useMock()
  }
})

watch(selectedZone, async (val) => {
  if (val) {
    try {
      const res = await getEcologyIndicators(val)
      indicators.value = res.data || []
      initHealthChart()
    } catch {}
  } else {
    try {
      const res = await getEcologyIndicators()
      indicators.value = res.data || []
      initHealthChart()
    } catch {}
  }
})

async function initHealthChart() {
  if (!healthChart.value) return
  const zone = selectedZone.value || indicators.value[0]?.zone_name || '大熊猫栖息地'
  let data = []
  try {
    const res = await getEcologyHistory(zone, 7)
    data = res.data || []
  } catch {
    data = []
    for (let i = 6; i >= 0; i--) {
      const d = new Date(Date.now() - i * 86400000)
      data.push({
        recorded_at: d.toISOString(),
        vegetation_coverage: 70 + Math.random() * 20,
        water_quality_index: 65 + Math.random() * 25,
        ecological_health_score: 70 + Math.random() * 20,
      })
    }
  }

  const chart = echarts.init(healthChart.value)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['健康评分', '植被覆盖', '水质指数'], bottom: 0 },
    xAxis: { type: 'category', data: data.map(d => d.recorded_at?.slice(5, 10) || ''), axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', min: 40, max: 100 },
    series: [
      { name: '健康评分', data: data.map(d => d.ecological_health_score), type: 'line', smooth: true, color: '#1890ff' },
      { name: '植被覆盖', data: data.map(d => d.vegetation_coverage), type: 'line', smooth: true, color: '#52c41a' },
      { name: '水质指数', data: data.map(d => d.water_quality_index), type: 'line', smooth: true, color: '#722ed1' },
    ],
    grid: { left: 40, right: 20, top: 10, bottom: 40 },
  })
}

function initRadarChart(data) {
  if (!radarChart.value) return
  const chart = echarts.init(radarChart.value)
  const indicators = data.indicators || []
  const series = data.series || []

  const colors = ['#1890ff', '#ff4d4f', '#52c41a', '#fa8c16', '#722ed1', '#13c2c2', '#f759ab', '#faad14']

  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: (p) => {
        if (p.seriesName) {
          let html = `<b>${p.seriesName}</b><br/>`
          const detail = series.find(s => s.name === p.seriesName)?.detail || {}
          if (detail.vegetation_coverage) html += `植被覆盖: ${detail.vegetation_coverage}<br/>`
          if (detail.water_quality_index) html += `水质指数: ${detail.water_quality_index}<br/>`
          if (detail.soil_health_index) html += `土壤健康: ${detail.soil_health_index}<br/>`
          if (detail.air_quality_index) html += `空气质量: ${detail.air_quality_index}<br/>`
          if (detail.species_diversity_index) html += `物种多样性: ${detail.species_diversity_index}<br/>`
          if (detail.ecological_health_score) html += `健康评分: ${detail.ecological_health_score}`
          return html
        }
        return `${p.name}: ${p.value}`
      },
    },
    legend: {
      data: series.map(s => s.name),
      bottom: 0,
      type: 'scroll',
    },
    radar: {
      center: ['50%', '50%'],
      radius: '65%',
      indicator: indicators.map(ind => ({
        name: ind.name,
        max: 100,
      })),
      axisName: { fontSize: 11, color: '#666' },
    },
    series: [{
      type: 'radar',
      data: series.map((s, i) => ({
        name: s.name,
        value: s.value,
        lineStyle: { color: colors[i % colors.length], width: 2 },
        areaStyle: { color: colors[i % colors.length], opacity: 0.05 },
        symbol: 'circle',
        symbolSize: 4,
        itemStyle: { color: colors[i % colors.length] },
      })),
    }],
  })
  setTimeout(() => chart.resize(), 100)
}

function useMock() {
  const names = ['三江源核心区', '大熊猫栖息地', '东北虎豹栖息地', '祁连山草甸区', '武夷山实验区', '海南热带雨林', '普达措湿地区', '可可西里荒野区']
  indicators.value = names.map((n, i) => ({
    id: i + 1, zone_name: n, zone_type: ['湿地','森林','森林','草原','森林','森林','湿地','高山'][i],
    vegetation_coverage: +(70 + Math.random() * 25).toFixed(1),
    species_richness: Math.floor(30 + Math.random() * 80),
    species_diversity_index: +(2 + Math.random() * 2).toFixed(2),
    water_quality_index: +(60 + Math.random() * 35).toFixed(1),
    soil_health_index: +(60 + Math.random() * 35).toFixed(1),
    air_quality_index: +(50 + Math.random() * 45).toFixed(1),
    carbon_sequestration: +(100 + Math.random() * 4900).toFixed(1),
    ecological_health_score: +(65 + Math.random() * 30).toFixed(1),
    anomaly_flag: Math.random() < 0.1,
    recorded_at: new Date().toISOString(),
  }))
  anomalies.value = indicators.value.filter(i => i.anomaly_flag)
  zoneOptions.value = names
  initHealthChart()

  const mockRadarIndicators = [
    { name: '植被覆盖', max: 100 },
    { name: '水质指数', max: 100 },
    { name: '土壤健康', max: 100 },
    { name: '空气质量', max: 100 },
    { name: '物种多样性', max: 100 },
    { name: '健康评分', max: 100 },
  ]
  const mockRadarSeries = names.map((n, i) => ({
    name: n,
    value: [
      Math.round(60 + Math.random() * 40),
      Math.round(50 + Math.random() * 50),
      Math.round(55 + Math.random() * 45),
      Math.round(45 + Math.random() * 55),
      Math.round(50 + Math.random() * 50),
      Math.round(60 + Math.random() * 40),
    ],
    detail: {
      vegetation_coverage: (70 + Math.random() * 25).toFixed(1),
      water_quality_index: (60 + Math.random() * 35).toFixed(1),
      soil_health_index: (60 + Math.random() * 35).toFixed(1),
      air_quality_index: (50 + Math.random() * 45).toFixed(1),
      species_diversity_index: (2 + Math.random() * 2).toFixed(2),
      ecological_health_score: (65 + Math.random() * 30).toFixed(1),
    },
  }))
  initRadarChart({ indicators: mockRadarIndicators, series: mockRadarSeries })
}

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}
</script>

<style scoped>
.anomaly-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}
.anomaly-card {
  height: 100%;
  overflow-y: auto;
}
.trend-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.trend-card .card-title { flex-shrink: 0; }
</style>
