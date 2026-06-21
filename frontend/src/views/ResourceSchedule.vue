<template>
  <div class="resource-page">
    <el-row :gutter="16" class="resource-top-row">
      <el-col :span="14" class="resource-left-col">
        <div class="dashboard-card schedule-card" ref="scheduleCardRef">
          <div class="card-title"><el-icon><List /></el-icon> 巡护调度计划</div>
          <el-table :data="schedules" stripe size="small" :max-height="tableMaxHeight">
            <el-table-column prop="patrol_team" label="巡护队伍" width="120" />
            <el-table-column prop="zone_name" label="负责区域" width="140" />
            <el-table-column prop="team_size" label="人数" width="60" />
            <el-table-column label="配备车辆" width="180">
              <template #default="{ row }">
                <el-tag v-for="v in (row.vehicles || [])" :key="v" size="small" style="margin:0 2px">{{ v }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="配备装备" min-width="200">
              <template #default="{ row }">
                <el-tag v-for="e in (row.equipment || [])" :key="e" size="small" style="margin:0 2px" type="info">{{ e }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="schedule_date" label="调度日期" width="160">
              <template #default="{ row }">{{ formatTime(row.schedule_date) }}</template>
            </el-table-column>
            <el-table-column prop="shift" label="班次" width="80">
              <template #default="{ row }">
                <el-tag size="small" :type="row.shift === 'night' ? 'danger' : row.shift === 'morning' ? 'success' : 'warning'">
                  {{ shiftLabel(row.shift) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="90">
              <template #default="{ row }">
                <el-tag size="small" :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :span="10">
        <div class="dashboard-card" style="margin-bottom:16px">
          <div class="card-title"><el-icon><UserFilled /></el-icon> 游客流量统计</div>
          <div v-for="v in visitors" :key="v.zone_name" class="visitor-item">
            <div class="visitor-name">
              <span>{{ v.zone_name }}</span>
              <el-tag v-if="v.needs_restriction" type="danger" size="small">需限流</el-tag>
            </div>
            <el-progress :percentage="Math.round(v.congestion * 100)" :stroke-width="12" :color="v.congestion > 0.8 ? '#ff4d4f' : v.congestion > 0.6 ? '#faad14' : '#52c41a'">
              <span style="font-size:11px">{{ v.current_visitors }} / {{ v.capacity }}</span>
            </el-progress>
          </div>
        </div>
        <div class="dashboard-card">
          <div class="card-title"><el-icon><Setting /></el-icon> 资源配置优化建议</div>
          <div ref="allocChart" style="height:200px"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="16" style="margin-top:16px">
      <el-col :span="24">
        <div class="dashboard-card">
          <div class="card-title">
            <el-icon><Connection /></el-icon> 资源调度流向图（桑基图）
            <span style="font-size:12px;color:#999;margin-left:8px">展示队伍、车辆、装备向各园区的资源分配流向</span>
          </div>
          <div ref="sankeyChart" style="height:380px"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getSchedules, getVisitorStats, optimizeAllocation, getResourceFlow } from '../api'

const schedules = ref([])
const visitors = ref([])
const allocations = ref([])
const allocChart = ref(null)
const sankeyChart = ref(null)
const scheduleCardRef = ref(null)
const tableMaxHeight = ref(320)

const shiftLabel = (s) => ({ morning: '早班', afternoon: '午班', night: '晚班' }[s] || s)
const statusLabel = (s) => ({ scheduled: '已排班', in_progress: '执行中', completed: '已完成' }[s] || s)
const statusType = (s) => ({ scheduled: 'info', in_progress: 'warning', completed: 'success' }[s] || 'info')

function updateTableHeight() {
  if (!scheduleCardRef.value) return
  const cardHeight = scheduleCardRef.value.offsetHeight
  const titleHeight = scheduleCardRef.value.querySelector('.card-title')?.offsetHeight || 0
  const padding = 36
  tableMaxHeight.value = Math.max(200, cardHeight - titleHeight - padding)
}

onMounted(async () => {
  try {
    const [sRes, vRes, aRes, fRes] = await Promise.all([
      getSchedules(20), getVisitorStats(), optimizeAllocation(), getResourceFlow()
    ])
    schedules.value = sRes.data || []
    visitors.value = vRes.data || []
    allocations.value = aRes.data || []
    initAllocChart()
    initSankeyChart(fRes.data || { nodes: [], links: [] })
  } catch {
    useMock()
  }
  nextTick(() => updateTableHeight())
  window.addEventListener('resize', updateTableHeight)
})

function initAllocChart() {
  if (!allocChart.value) return
  const chart = echarts.init(allocChart.value)
  const data = allocations.value.length > 0 ? allocations.value : useMockAlloc()
  chart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { data: ['当前队伍', '建议队伍'], bottom: 0 },
    xAxis: { type: 'category', data: data.map(d => d.zone_name), axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: 'value', name: '队伍数' },
    series: [
      { name: '当前队伍', type: 'bar', data: data.map(d => d.current_teams), color: '#1890ff' },
      { name: '建议队伍', type: 'bar', data: data.map(d => d.suggested_teams), color: '#ff4d4f' },
    ],
    grid: { left: 40, right: 20, top: 10, bottom: 50 },
  })
}

function initSankeyChart(data) {
  if (!sankeyChart.value) return
  const chart = echarts.init(sankeyChart.value)

  const nodes = (data.nodes || []).map(n => ({
    name: n.name,
    itemStyle: {
      color: n.name.includes('[车辆]') ? '#fa8c16' : n.name.includes('[装备]') ? '#722ed1' : '#1890ff',
    },
  }))
  const links = (data.links || []).map(l => ({
    source: l.source,
    target: l.target,
    value: l.value,
  }))

  chart.setOption({
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
    },
    series: [{
      type: 'sankey',
      layout: 'none',
      emphasis: { focus: 'adjacency' },
      nodeAlign: 'left',
      layoutIterations: 0,
      data: nodes,
      links: links,
      label: {
        fontSize: 11,
        color: '#333',
      },
      lineStyle: {
        color: 'gradient',
        curveness: 0.5,
      },
    }],
  })
  setTimeout(() => chart.resize(), 100)
}

function useMockAlloc() {
  return [
    { zone_name: '三江源核心区', current_teams: 2, suggested_teams: 5 },
    { zone_name: '大熊猫栖息地', current_teams: 3, suggested_teams: 3 },
    { zone_name: '东北虎豹栖息地', current_teams: 2, suggested_teams: 4 },
    { zone_name: '祁连山草甸区', current_teams: 1, suggested_teams: 2 },
    { zone_name: '可可西里荒野区', current_teams: 1, suggested_teams: 4 },
  ]
}

function useMock() {
  const teams = ['巡护一队', '巡护二队', '巡护三队', '无人机巡检队', '科研监测队']
  const zones = ['三江源核心区', '大熊猫栖息地', '东北虎豹栖息地', '祁连山草甸区', '武夷山实验区', '海南热带雨林', '可可西里荒野区']
  schedules.value = []
  for (let i = 0; i < 12; i++) {
    schedules.value.push({
      id: i + 1, patrol_team: teams[i % 5], team_size: 3 + (i % 6),
      zone_name: zones[i % 7],
      vehicles: ['全地形车', '无人机'].slice(0, 1 + (i % 2)),
      equipment: ['GPS定位仪', '红外相机', '灭火器', '急救包', '对讲机'].slice(0, 2 + (i % 4)),
      schedule_date: new Date(Date.now() + i * 3600000).toISOString(),
      shift: ['morning', 'afternoon', 'night'][i % 3],
      status: ['scheduled', 'in_progress', 'completed'][i % 3],
    })
  }
  visitors.value = zones.slice(0, 5).map(z => {
    const cap = Math.floor(500 + Math.random() * 3000)
    const cur = Math.floor(cap * (0.1 + Math.random() * 0.8))
    return {
      zone_name: z, current_visitors: cur, capacity: cap,
      congestion: +(cur / cap).toFixed(2), needs_restriction: cur / cap > 0.8,
    }
  })
  allocations.value = useMockAlloc()
  initAllocChart()

  const mockNodes = [
    { name: '巡护一队' }, { name: '巡护二队' }, { name: '巡护三队' },
    { name: '无人机巡检队' }, { name: '科研监测队' },
    { name: '[车辆]全地形车' }, { name: '[车辆]无人机' },
    { name: '[装备]GPS定位仪' }, { name: '[装备]红外相机' }, { name: '[装备]灭火器' },
    { name: '[装备]急救包' }, { name: '[装备]对讲机' },
    ...zones.map(z => ({ name: z })),
  ]
  const mockLinks = [
    { source: '巡护一队', target: '大熊猫栖息地', value: 5 },
    { source: '巡护二队', target: '三江源核心区', value: 4 },
    { source: '巡护三队', target: '东北虎豹栖息地', value: 6 },
    { source: '无人机巡检队', target: '祁连山草甸区', value: 3 },
    { source: '无人机巡检队', target: '可可西里荒野区', value: 3 },
    { source: '科研监测队', target: '武夷山实验区', value: 4 },
    { source: '科研监测队', target: '海南热带雨林', value: 3 },
    { source: '[车辆]全地形车', target: '大熊猫栖息地', value: 2 },
    { source: '[车辆]全地形车', target: '可可西里荒野区', value: 1 },
    { source: '[车辆]无人机', target: '三江源核心区', value: 1 },
    { source: '[车辆]无人机', target: '祁连山草甸区', value: 1 },
    { source: '[装备]GPS定位仪', target: '大熊猫栖息地', value: 3 },
    { source: '[装备]GPS定位仪', target: '东北虎豹栖息地', value: 2 },
    { source: '[装备]红外相机', target: '东北虎豹栖息地', value: 1 },
    { source: '[装备]红外相机', target: '海南热带雨林', value: 1 },
    { source: '[装备]灭火器', target: '祁连山草甸区', value: 2 },
    { source: '[装备]急救包', target: '大熊猫栖息地', value: 2 },
    { source: '[装备]急救包', target: '可可西里荒野区', value: 1 },
    { source: '[装备]对讲机', target: '三江源核心区', value: 2 },
    { source: '[装备]对讲机', target: '武夷山实验区', value: 1 },
  ]
  initSankeyChart({ nodes: mockNodes, links: mockLinks })
}

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString('zh-CN')
}
</script>

<style scoped>
.resource-top-row :deep(.el-col) {
  display: flex;
  flex-direction: column;
}
.resource-left-col {
  display: flex;
}
.schedule-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.schedule-card .card-title { flex-shrink: 0; }
.visitor-item { margin-bottom: 12px; }
.visitor-name { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; font-weight: 600; font-size: 14px; }
</style>
