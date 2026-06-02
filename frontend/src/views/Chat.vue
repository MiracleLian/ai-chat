<template>
  <div class="chat-layout">
    <!-- 顶部导航 -->
    <el-header class="chat-header">
      <div class="header-left">
        <div class="logo-icon">🤖</div>
        <div class="logo-text">
          <h3>AI 智能问答</h3>
          <span class="model-badge">DeepSeek-V4</span>
        </div>
      </div>
      <div class="header-right">
        <el-badge :value="messages.length" :max="99" class="msg-count" v-if="messages.length">
          <el-button text @click="$router.push('/history')">
            <el-icon><Clock /></el-icon> 历史记录
          </el-button>
        </el-badge>
        <el-button text @click="$router.push('/history')" v-else>
          <el-icon><Clock /></el-icon> 历史记录
        </el-button>
        <el-button text @click="$router.push('/userinfo')">
          <el-icon><User /></el-icon> 个人信息
        </el-button>
        <el-button text type="warning" @click="showAdminDialog = true" title="管理员配置">
          ⚙️
        </el-button>
        <el-button text type="danger" @click="handleLogout">
          <el-icon><SwitchButton /></el-icon> 退出
        </el-button>
      </div>
    </el-header>

    <!-- 管理员登录弹窗 -->
    <el-dialog v-model="showAdminDialog" title="管理员验证" width="380px" :close-on-click-modal="false">
      <el-form :model="adminForm" @submit.prevent="handleAdminLogin">
        <el-form-item label="管理员账号">
          <el-input v-model="adminForm.username" placeholder="请输入管理员账号" prefix-icon="User" />
        </el-form-item>
        <el-form-item label="管理员密码">
          <el-input v-model="adminForm.password" type="password" placeholder="请输入管理员密码" prefix-icon="Lock" show-password @keydown.enter="handleAdminLogin" />
        </el-form-item>
        <el-button type="warning" :loading="adminLoading" style="width:100%" @click="handleAdminLogin">
          验证并进入配置
        </el-button>
      </el-form>
    </el-dialog>

    <!-- 对话区域 -->
    <main class="chat-main" ref="chatMainRef">
      <div v-if="messages.length === 0" class="welcome-area">
        <div class="welcome-icon">✨</div>
        <h2>你好！有什么可以帮你？</h2>
        <p class="welcome-sub">我是基于 DeepSeek 大模型的 AI 助手，可以回答问题、写代码、翻译等</p>
        <div class="quick-prompts">
          <span
            v-for="p in quickPrompts"
            :key="p"
            class="quick-prompt-tag"
            @click="quickSend(p)"
          >{{ p }}</span>
        </div>
      </div>

      <div class="messages-container" v-else>
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['message-row', msg.role === 'user' ? 'user-row' : 'ai-row']"
        >
          <div class="msg-avatar" v-if="msg.role === 'ai'">🤖</div>
          <div :class="['message-bubble', msg.role === 'user' ? 'user-bubble' : 'ai-bubble']">
            <div
              v-if="msg.role === 'ai' && !msg.error"
              class="bubble-content markdown-body"
              v-html="renderMarkdown(msg.content)"
            ></div>
            <div v-else class="bubble-content">{{ msg.content }}</div>
            <div class="bubble-footer">
              <span class="bubble-time">{{ msg.time }}</span>
              <template v-if="msg.role === 'user'">
                <el-button text size="small" class="copy-btn" @click="copyText(msg.content)">
                  <el-icon><DocumentCopy /></el-icon>
                </el-button>
              </template>
              <template v-if="msg.error">
                <el-button text size="small" type="danger" @click="retry(msg)">
                  <el-icon><RefreshRight /></el-icon> 重试
                </el-button>
              </template>
            </div>
          </div>
          <div class="msg-avatar" v-if="msg.role === 'user'">
            <el-avatar :size="32" icon="User" />
          </div>
        </div>

        <!-- AI思考中 -->
        <div v-if="isLoading" class="message-row ai-row">
          <div class="msg-avatar">🤖</div>
          <div class="message-bubble ai-bubble thinking-bubble">
            <div class="thinking-dots">
              <span></span><span></span><span></span>
            </div>
            <span class="thinking-text">AI 正在思考中...</span>
          </div>
        </div>
      </div>
    </main>

    <!-- 输入区域 -->
    <footer class="chat-footer">
      <div class="input-area">
        <el-input
          v-model="question"
          type="textarea"
          :rows="2"
          placeholder="输入你的问题，Enter 发送 / Shift+Enter 换行..."
          resize="none"
          :disabled="isLoading"
          @keydown.enter.exact="handleSend"
        />
        <div class="input-actions">
          <el-button @click="clearMessages" :disabled="messages.length === 0" text>
            <el-icon><Delete /></el-icon> 清屏
          </el-button>
          <span class="char-count" v-if="question.length > 1800" :class="{ warn: question.length > 2000 }">
            {{ question.length }}/2000
          </span>
          <el-button
            type="primary"
            @click="handleSend"
            :loading="isLoading"
            :disabled="!question.trim()"
          >
            <el-icon><Promotion /></el-icon> 发送
          </el-button>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const auth = useAuthStore()

const question = ref('')
const messages = ref([])
const isLoading = ref(false)
const chatMainRef = ref(null)

// 管理员弹窗
const showAdminDialog = ref(false)
const adminLoading = ref(false)
const adminForm = reactive({ username: '', password: '' })

async function handleAdminLogin() {
  if (!adminForm.username || !adminForm.password) {
    ElMessage.warning('请输入管理员账号和密码')
    return
  }
  adminLoading.value = true
  try {
    await api.post('/admin/login', { ...adminForm })
    localStorage.setItem('admin_verified', '1')
    adminForm.username = ''
    adminForm.password = ''
    showAdminDialog.value = false
    ElMessage.success('验证成功')
    router.push('/admin')
  } catch {
    ElMessage.error('管理员账号或密码错误')
  } finally {
    adminLoading.value = false
  }
}

const quickPrompts = [
  '用 Python 写一个冒泡排序',
  '解释一下什么是 RESTful API',
  '帮我翻译一段中文到英文',
  '推荐 3 本编程入门书籍',
]

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true,
})

function renderMarkdown(text) {
  if (!text) return ''
  try {
    return marked.parse(text)
  } catch {
    return text
  }
}

function getNowTime() {
  return new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function scrollToBottom() {
  nextTick(() => {
    if (chatMainRef.value) {
      chatMainRef.value.scrollTo({ top: chatMainRef.value.scrollHeight, behavior: 'smooth' })
    }
  })
}

function quickSend(prompt) {
  question.value = prompt
  handleSend()
}

async function handleSend() {
  const q = question.value.trim()
  if (!q || isLoading.value) return
  if (q.length > 2000) {
    ElMessage.warning('问题不能超过 2000 个字符')
    return
  }

  const msgIdx = messages.value.length
  messages.value.push({ role: 'user', content: q, time: getNowTime() })
  question.value = ''
  scrollToBottom()

  isLoading.value = true
  try {
    const { data } = await api.post('/chat/send', { question: q })
    messages.value.push({ role: 'ai', content: data.answer, time: getNowTime(), error: false })
  } catch {
    messages.value.push({
      role: 'ai',
      content: '请求失败，请检查网络连接后重试。',
      time: getNowTime(),
      error: true,
      retryQuestion: q,
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

async function retry(msg) {
  if (isLoading.value) return
  const q = msg.retryQuestion
  // 找到并移除失败的消息
  const idx = messages.value.indexOf(msg)
  if (idx >= 0) messages.value.splice(idx, 1)

  isLoading.value = true
  try {
    const { data } = await api.post('/chat/send', { question: q })
    messages.value.push({ role: 'ai', content: data.answer, time: getNowTime(), error: false })
  } catch {
    messages.value.push({
      role: 'ai',
      content: '请求失败，请检查网络连接后重试。',
      time: getNowTime(),
      error: true,
      retryQuestion: q,
    })
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

function clearMessages() {
  messages.value = []
}

async function handleLogout() {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
    auth.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  } catch { /* 取消 */ }
}
</script>

<style scoped>
.chat-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f0f2f5;
}

/* ── Header ── */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0 24px;
  height: 60px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon { font-size: 28px; }

.logo-text h3 {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  line-height: 1.2;
}

.model-badge {
  font-size: 11px;
  color: rgba(255,255,255,.7);
  background: rgba(255,255,255,.15);
  padding: 1px 8px;
  border-radius: 10px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 2px;
}

.header-right .el-button { color: #fff; }
.header-right .el-button:hover { background: rgba(255,255,255,.15) !important; }
.header-right .el-button--danger { color: rgba(255,200,200,1); }

/* ── Main ── */
.chat-main {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}

/* 欢迎区 */
.welcome-area {
  max-width: 600px;
  margin: 80px auto 0;
  text-align: center;
}

.welcome-icon { font-size: 64px; margin-bottom: 16px; animation: float 3s ease-in-out infinite; }

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.welcome-area h2 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 8px;
}

.welcome-sub {
  color: #909399;
  font-size: 14px;
  margin-bottom: 32px;
}

.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.quick-prompt-tag {
  display: inline-block;
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 20px;
  color: #606266;
  font-size: 13px;
  cursor: pointer;
  transition: all .2s;
}

.quick-prompt-tag:hover {
  border-color: #667eea;
  color: #667eea;
  background: #f0f2ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102,126,234,.15);
}

/* 消息列表 */
.messages-container {
  max-width: 820px;
  margin: 0 auto;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 20px;
  animation: msgIn .3s ease-out;
}

@keyframes msgIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.user-row { justify-content: flex-end; }
.ai-row { justify-content: flex-start; }

.msg-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.message-bubble {
  max-width: 75%;
  padding: 14px 18px;
  border-radius: 16px;
  line-height: 1.65;
  word-break: break-word;
  position: relative;
}

.user-bubble {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.ai-bubble {
  background: #fff;
  color: #303133;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 6px rgba(0,0,0,.06);
}

.thinking-bubble {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
}

.thinking-dots {
  display: flex;
  gap: 4px;
}

.thinking-dots span {
  width: 8px;
  height: 8px;
  background: #909399;
  border-radius: 50%;
  animation: dotBounce 1.4s infinite ease-in-out both;
}

.thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
.thinking-dots span:nth-child(2) { animation-delay: -0.16s; }
.thinking-dots span:nth-child(3) { animation-delay: 0; }

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

.thinking-text {
  color: #909399;
  font-size: 14px;
}

.bubble-footer {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 6px;
  justify-content: flex-end;
}

.user-bubble .bubble-footer { justify-content: flex-end; }
.ai-bubble .bubble-footer { justify-content: flex-start; }

.bubble-time {
  font-size: 11px;
  opacity: 0.55;
}

.user-bubble .bubble-time { color: rgba(255,255,255,.7); }
.ai-bubble .bubble-time { color: #909399; }

.copy-btn {
  opacity: 0;
  transition: opacity .2s;
  padding: 2px !important;
  font-size: 13px;
}

.message-bubble:hover .copy-btn { opacity: 1; }

.user-bubble .copy-btn { color: rgba(255,255,255,.7) !important; }
.user-bubble .copy-btn:hover { color: #fff !important; background: rgba(255,255,255,.15) !important; }

/* Markdown styles */
.markdown-body :deep(p) { margin: 0 0 8px; }
.markdown-body :deep(p:last-child) { margin-bottom: 0; }
.markdown-body :deep(pre) {
  background: #f6f8fa;
  border-radius: 8px;
  padding: 12px 16px;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.5;
  margin: 8px 0;
}
.markdown-body :deep(code) {
  font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
}
.markdown-body :deep(p code) {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  color: #e74c3c;
}
.markdown-body :deep(ul), .markdown-body :deep(ol) {
  padding-left: 20px;
  margin: 6px 0;
}
.markdown-body :deep(li) { margin-bottom: 4px; }
.markdown-body :deep(blockquote) {
  border-left: 3px solid #667eea;
  padding-left: 12px;
  color: #606266;
  margin: 8px 0;
}
.markdown-body :deep(table) {
  border-collapse: collapse;
  margin: 8px 0;
  width: 100%;
}
.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #e4e7ed;
  padding: 8px 12px;
  text-align: left;
}
.markdown-body :deep(th) { background: #f5f7fa; font-weight: 600; }
.markdown-body :deep(h1), .markdown-body :deep(h2), .markdown-body :deep(h3) {
  margin: 12px 0 8px;
}

/* ── Footer ── */
.chat-footer {
  background: #fff;
  border-top: 1px solid #e4e7ed;
  padding: 14px 24px;
}

.input-area {
  max-width: 820px;
  margin: 0 auto;
}

.input-area :deep(.el-textarea__inner) {
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  transition: border-color .2s;
}
.input-area :deep(.el-textarea__inner:focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102,126,234,.15);
}

.input-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.char-count {
  font-size: 12px;
  color: #909399;
}

.char-count.warn { color: #f56c6c; }

/* ── Scrollbar ── */
.chat-main::-webkit-scrollbar { width: 6px; }
.chat-main::-webkit-scrollbar-track { background: transparent; }
.chat-main::-webkit-scrollbar-thumb { background: #c0c4cc; border-radius: 3px; }
.chat-main::-webkit-scrollbar-thumb:hover { background: #909399; }
</style>
