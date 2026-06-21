import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
  },
  {
    path: '/ecology',
    name: 'Ecology',
    component: () => import('../views/EcologyMonitor.vue'),
  },
  {
    path: '/fire',
    name: 'Fire',
    component: () => import('../views/FireControl.vue'),
  },
  {
    path: '/risk',
    name: 'Risk',
    component: () => import('../views/RiskWarning.vue'),
  },
  {
    path: '/resource',
    name: 'Resource',
    component: () => import('../views/ResourceSchedule.vue'),
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/AIChat.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
