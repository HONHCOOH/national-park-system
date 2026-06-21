<template>
  <div id="app-container">
    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <h1>国家公园智能决策支持系统</h1>
          <el-tag type="success" size="small">智能监测中</el-tag>
        </div>
        <div class="header-right">
          <el-space>
            <span style="color:#fff;font-size:14px">今天 {{ today }}</span>
            <el-button type="primary" link style="color:#fff" @click="$router.push('/chat')">
              <el-icon><ChatDotRound /></el-icon> AI助手
            </el-button>
          </el-space>
        </div>
      </el-header>

      <el-container>
        <el-aside width="220px" class="app-sidebar">
          <el-menu
            :default-active="activeMenu"
            router
            background-color="#001529"
            text-color="#ffffffa6"
            active-text-color="#fff"
          >
            <el-menu-item index="/">
              <el-icon><DataBoard /></el-icon>
              <span>系统概览</span>
            </el-menu-item>
            <el-sub-menu index="modules">
              <template #title>
                <el-icon><Monitor /></el-icon>
                <span>功能模块</span>
              </template>
              <el-menu-item index="/ecology">
                <el-icon><Sunny /></el-icon>
                <span>生态态势感知</span>
              </el-menu-item>
              <el-menu-item index="/fire">
                <el-icon><WarningFilled /></el-icon>
                <span>火灾防治管控</span>
              </el-menu-item>
              <el-menu-item index="/risk">
                <el-icon><BellFilled /></el-icon>
                <span>风险预警响应</span>
              </el-menu-item>
              <el-menu-item index="/resource">
                <el-icon><Setting /></el-icon>
                <span>资源协同调度</span>
              </el-menu-item>
            </el-sub-menu>
            <el-menu-item index="/chat">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI决策助手</span>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main class="app-main">
          <router-view v-slot="{ Component, route: r }">
            <transition
              :name="transitionName"
              @after-enter="onAfterEnter"
              mode="out-in"
            >
              <component :is="Component" :key="r.path" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useFirstVisit } from './composables/useFirstVisit.js'

const route = useRoute()
const activeMenu = computed(() => route.path)
const today = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })

const { transitionName, onAfterEnter } = useFirstVisit()
</script>

<style scoped>
#app-container {
  height: 100vh;
  overflow: hidden;
}
.app-header {
  background: linear-gradient(135deg, #001529 0%, #003a70 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px !important;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-left h1 {
  color: #fff;
  font-size: 18px;
  margin: 0;
  font-weight: 600;
}
.app-sidebar {
  background: #001529;
  overflow-y: auto;
  height: calc(100vh - 60px);
}
.app-main {
  background: #f0f2f5;
  height: calc(100vh - 60px);
  overflow-y: auto;
  padding: 20px;
}
</style>
