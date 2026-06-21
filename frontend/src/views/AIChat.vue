<template>
  <div class="chat-page">
    <el-row :gutter="16">
      <el-col :span="16">
        <div class="dashboard-card chat-container">
          <div class="card-title">
            <el-icon><ChatDotRound /></el-icon> AI决策助手
            <el-tag size="small" type="success" style="margin-left:8px">LLM 驱动</el-tag>
          </div>

          <div class="chat-messages" ref="chatMessages">
            <div v-if="messages.length === 0" class="chat-welcome">
              <div class="welcome-icon"><el-icon :size="48"><ChatDotRound /></el-icon></div>
              <h3>国家公园智能决策助手</h3>
              <p>我可以帮您分析生态数据、评估火灾风险、制定应急预案、优化资源调度。请在下方输入您的问题。</p>
            </div>

            <div v-for="(msg, i) in messages" :key="i" :class="['chat-message', msg.role]">
              <div class="message-avatar">
                <el-icon v-if="msg.role === 'ai'" :size="20"><Monitor /></el-icon>
                <el-icon v-else :size="20"><UserFilled /></el-icon>
              </div>
              <div class="message-content">
                <div class="message-text" v-html="formatMsg(msg.content)"></div>
                <div class="message-time">{{ msg.time }}</div>
              </div>
            </div>
          </div>

          <div class="chat-input">
            <el-input
              v-model="inputText"
              placeholder="输入您的问题，例如：分析当前火灾风险最高的区域，并给出应对建议"
              @keyup.enter="sendMessage"
              :disabled="loading"
              size="large"
            >
              <template #suffix>
                <el-button type="primary" :icon="Promotion" @click="sendMessage" :loading="loading">
                  发送
                </el-button>
              </template>
            </el-input>
          </div>
        </div>
      </el-col>

      <el-col :span="8">
        <div class="dashboard-card" style="margin-bottom:12px">
          <div class="card-title"><el-icon><Lightning /></el-icon> 快捷提问</div>
          <div class="quick-questions">
            <el-tag
              v-for="q in quickQuestions"
              :key="q"
              class="quick-tag"
              @click="sendQuick(q)"
              effect="plain"
              type="info"
            >
              {{ q }}
            </el-tag>
          </div>
        </div>

        <div class="dashboard-card">
          <div class="card-title"><el-icon><InfoFilled /></el-icon> 关于AI助手</div>
          <div class="about-ai">
            <p>本AI助手基于大语言模型，整合了以下能力：</p>
            <ul>
              <li>生态监测数据分析</li>
              <li>火灾风险评估与建议</li>
              <li>应急方案生成</li>
              <li>资源调度优化</li>
              <li>自然语言交互查询</li>
            </ul>
            <p style="margin-top:8px;color:#999;font-size:12px">
              当前使用 {{ modelInfo }} 模型<br/>
              支持 OpenA I/Ollama/DeepSeek 等接口
            </p>
            <p style="color:#999;font-size:11px">
              数据来源：系统模拟数据库 + 生态学知识库
            </p>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useChatStore } from '../stores/chat'
import { chatWithAI } from '../api'
import { ElMessage } from 'element-plus'
import { Promotion } from '@element-plus/icons-vue'

const store = useChatStore()
const messages = store.messages
const loading = store.loading
const inputText = ref('')
const chatMessages = ref(null)
const modelInfo = ref('本地/Qwen')

const quickQuestions = [
  '分析当前系统的生态健康状况',
  '哪些区域的火灾风险最高？',
  '如何优化巡护资源分配？',
  '当前有哪些活跃预警？',
  '建议加强哪些方面的生态监测？',
  '评估气候变化对园区的影响',
]

function sendMessage() {
  const text = inputText.value.trim()
  if (!text || loading.value) return
  sendMsg(text)
  inputText.value = ''
}

function sendQuick(q) {
  if (loading.value) return
  sendMsg(q)
}

async function sendMsg(text) {
  if (loading.value) return
  store.addMessage('user', text)
  store.loading = true
  scrollToBottom()

  try {
    const res = await chatWithAI(text)
    store.addMessage('ai', res.data?.reply || '抱歉，AI回复异常。')
  } catch {
    store.addMessage('ai', getMockReply(text))
    ElMessage.warning('AI服务未连接，使用本地规则回复')
  }

  store.loading = false
  scrollToBottom()
}

function getMockReply(text) {
  if (text.includes('火灾') || text.includes('火险')) {
    return `【火灾风险分析报告】\n\n基于多方数据分析，当前系统火灾风险评估如下：\n\n1. <strong>高风险区域</strong>：祁连山草甸区（风险评分 82.3，极高风险），主要原因是干旱指数高（88.2）、风速大（22.1 m/s）、植被类型为易燃草原。\n\n2. <strong>中高风险区域</strong>：大熊猫栖息地（风险评分 68.5，高风险），气温34.2°C、湿度仅25.3%。\n\n3. <strong>低风险区域</strong>：海南热带雨林（风险评分 18.7）、三江源核心区（42.1）。\n\n<strong>建议措施：</strong>\n• 立即向祁连山草甸区增派巡护力量\n• 启动无人机24小时连续监测\n• 检查防火隔离带完整性\n• 提前预置灭火装备至储备点`
  }
  if (text.includes('生态') || text.includes('健康')) {
    return `【生态健康分析报告】\n\n当前系统监测8个国家公园区域，整体生态健康状况良好：\n\n1. <strong>平均健康评分</strong>：78.5分（满分100），处于健康水平。\n\n2. <strong>最佳区域</strong>：海南热带雨林（90分）、大熊猫栖息地（88分）、武夷山实验区（85分）\n\n3. <strong>需关注区域</strong>：祁连山草甸区（71分），植被覆盖度有下降趋势；可可西里荒野区（74分），物种多样性指数偏低\n\n4. <strong>异常指标</strong>：检测到2处异常，主要在草甸区植被退化和湿地水位变化。\n\n<strong>建议措施：</strong>\n• 加强祁连山草甸区生态修复\n• 在可可西里增设红外相机监测点\n• 关注气候变化对湿地的影响`
  }
  if (text.includes('资源') || text.includes('调度') || text.includes('巡护')) {
    return `【资源调度优化建议】\n\n根据当前各区域风险评估和资源部署情况：\n\n1. <strong>资源缺口</strong>：\n   • 三江源核心区：当前2队，建议5队（面积大、保护级别高）\n   • 可可西里荒野区：当前1队，建议4队\n   • 东北虎豹栖息地：当前2队，建议4队\n\n2. <strong>无人机调度</strong>：建议将无人机群的40%部署至高火险区域，30%覆盖核心保护区，30%用于常规巡护。\n\n3. <strong>巡护路线优化</strong>：基于风险等级动态调整路线，高火险期增加夜间巡逻班次。\n\n4. <strong>游客管理</strong>：监测到部分区域游客流量接近承载上限，建议在高峰时段实施预约限流。`
  }
  if (text.includes('预警') || text.includes('风险')) {
    return `【风险预警状态】\n\n当前系统共有4个活跃预警：\n\n1. 🔴 <strong>红色预警</strong>（1个）：祁连山草甸极高火险\n2. 🟠 <strong>橙色预警</strong>（1个）：大熊猫栖息地高温干旱火险\n3. 🟡 <strong>黄色预警</strong>（1个）：松材线虫病扩散预警\n4. 🔵 <strong>蓝色预警</strong>（1个）：游客违规进入核心区\n\n<strong>建议优先处理红色和橙色预警</strong>，已生成相应应急预案。`
  }
  return `【综合回复】\n\n关于"${text}"的分析：\n\n这是一个关于国家公园管理的专业问题。基于系统中的人工智能分析引擎，建议从以下几个方面考虑：\n\n1. 生态数据综合分析\n2. 风险评估与预警机制\n3. 资源调度优化\n4. 应急预案准备\n\n如需要更详细的分析，请提供具体区域名称或更精确的问题描述。`
}

function formatMsg(text) {
  return text.replace(/\n/g, '<br/>')
}

function scrollToBottom() {
  nextTick(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTop = chatMessages.value.scrollHeight
    }
  })
}

onMounted(() => {
  if (messages.length > 0) {
    scrollToBottom()
  }
})
</script>

<style scoped>
.chat-container { display: flex; flex-direction: column; height: calc(100vh - 110px); }
.chat-messages { flex: 1; overflow-y: auto; padding: 16px; background: #fafafa; border-radius: 8px; margin-bottom: 12px; }
.chat-welcome { text-align: center; padding: 60px 20px; color: #999; }
.welcome-icon { margin-bottom: 16px; color: #1890ff; }
.chat-welcome h3 { color: #333; margin-bottom: 8px; }
.chat-message { display: flex; gap: 12px; margin-bottom: 16px; }
.chat-message.ai { flex-direction: row; }
.chat-message.user { flex-direction: row-reverse; }
.message-avatar {
  width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.chat-message.ai .message-avatar { background: #e6f7ff; color: #1890ff; }
.chat-message.user .message-avatar { background: #f0f5ff; color: #52c41a; }
.message-content { max-width: 75%; }
.chat-message.ai .message-content { background: #fff; padding: 12px 16px; border-radius: 4px 16px 16px 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.chat-message.user .message-content { background: #1890ff; color: #fff; padding: 12px 16px; border-radius: 16px 4px 16px 16px; }
.message-text { font-size: 14px; line-height: 1.6; }
.message-time { font-size: 11px; color: #999; margin-top: 4px; }
.chat-message.user .message-time { color: rgba(255,255,255,0.7); }
.chat-input { padding-top: 8px; border-top: 1px solid #f0f0f0; }

.quick-questions { display: flex; flex-wrap: wrap; gap: 8px; }
.quick-tag { cursor: pointer; padding: 8px 12px; font-size: 13px; transition: all 0.2s; }
.quick-tag:hover { color: #1890ff; border-color: #1890ff; }

.about-ai { font-size: 13px; color: #666; line-height: 1.8; }
.about-ai ul { padding-left: 16px; }
.about-ai li { margin: 2px 0; }
</style>
