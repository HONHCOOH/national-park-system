import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export function getStats() {
  return api.get('/stats')
}

export function getZones() {
  return api.get('/zones')
}

export function getEcologyIndicators(zoneName) {
  const params = zoneName ? { zone_name: zoneName } : {}
  return api.get('/ecology/indicators', { params })
}

export function getEcologyHistory(zoneName, days = 7) {
  return api.get(`/ecology/indicators/${zoneName}/history`, { params: { days } })
}

export function getAnomalies(limit = 10) {
  return api.get('/ecology/anomalies', { params: { limit } })
}

export function getHealthTrend(days = 30) {
  return api.get('/ecology/health-trend', { params: { days } })
}

export function getFireRisks() {
  return api.get('/fire/risks')
}

export function getZoneFireRisk(zoneName) {
  return api.get(`/fire/risks/${zoneName}`)
}

export function optimizeRoutes(zoneName, teamCount = 1) {
  return api.post('/fire/routes/optimize', { zone_name: zoneName, team_count: teamCount })
}

export function simulateSpread(lat, lng, hours = 6) {
  return api.post('/fire/spread/simulate', { lat, lng, hours })
}

export function calculateFireRisk(data) {
  return api.post('/fire/risk/calculate', data)
}

export function getActiveAlerts() {
  return api.get('/risk/alerts')
}

export function getAlertHistory(limit = 20) {
  return api.get('/risk/alerts/history', { params: { limit } })
}

export function resolveAlert(alertId) {
  return api.post(`/risk/alerts/${alertId}/resolve`)
}

export function getAlertStats() {
  return api.get('/risk/stats')
}

export function getSchedules(limit = 20) {
  return api.get('/resource/schedules', { params: { limit } })
}

export function getVisitorStats() {
  return api.get('/resource/visitors')
}

export function optimizeAllocation() {
  return api.get('/resource/allocation/optimize')
}

export function getPatrolLogs(limit = 10) {
  return api.get('/resource/patrol-logs', { params: { limit } })
}

export function getRadarData() {
  return api.get('/ecology/radar')
}

export function getFireCorrelation() {
  return api.get('/fire/correlation')
}

export function getFireHeatmap() {
  return api.get('/fire/heatmap')
}

export function getAlertTimeline(limit = 30) {
  return api.get('/risk/timeline', { params: { limit } })
}

export function getResourceFlow() {
  return api.get('/resource/flow')
}

export function chatWithAI(message) {
  return api.post('/chat', { message })
}

export default api
