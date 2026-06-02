<template>
  <div class="admin-layout">
    <!-- 顶部导航 -->
    <el-header class="page-header">
      <div class="header-left">
        <el-button text @click="$router.push('/')">
          <el-icon><ArrowLeft /></el-icon> 返回对话
        </el-button>
        <div class="header-divider"></div>
        <h3>🛠️ 管理员配置</h3>
      </div>
      <div class="header-right">
        <el-button text type="danger" @click="handleLogout">退出管理</el-button>
      </div>
    </el-header>

    <main class="page-main">
      <el-card class="config-card" shadow="hover">
        <template #header>
          <div class="card-title">
            <span>🤖 AI 模型配置</span>
            <el-tag v-if="saved" type="success" size="small" effect="dark">已保存</el-tag>
          </div>
        </template>

        <el-form :model="form" label-position="top" ref="formRef">
          <el-form-item label="API 地址 (AI_API_URL)">
            <el-input v-model="form.AI_API_URL" placeholder="https://api.deepseek.com/anthropic/v1/messages" />
            <div class="form-hint">Anthropic Messages API 兼容接口地址</div>
          </el-form-item>

          <el-form-item label="API 密钥 (AI_API_KEY)">
            <el-input v-model="form.AI_API_KEY" type="password" show-password placeholder="sk-..." />
            <div class="form-hint">API 密钥，保存后不会完全显示</div>
          </el-form-item>

          <el-form-item label="模型名称 (AI_MODEL)">
            <el-input v-model="form.AI_MODEL" placeholder="DeepSeek-V4-pro" />
            <div class="form-hint">模型 ID，如 DeepSeek-V4-pro / DeepSeek-V3.2 等</div>
          </el-form-item>

          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="温度 (AI_TEMPERATURE)">
                <el-slider v-model="form.AI_TEMPERATURE" :min="0" :max="1" :step="0.1" show-input />
                <div class="form-hint">0=严谨, 1=创意</div>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="最大 Token (AI_MAX_TOKENS)">
                <el-input-number v-model="form.AI_MAX_TOKENS" :min="256" :max="8192" :step="256" controls-position="right" style="width:100%" />
                <div class="form-hint">回复最大长度</div>
              </el-form-item>
            </el-col>
          </el-row>

          <el-form-item label="系统提示词 (AI_SYSTEM_PROMPT)">
            <el-input v-model="form.AI_SYSTEM_PROMPT" type="textarea" :rows="3" placeholder="你是一个智能助手..." />
            <div class="form-hint">定义 AI 的角色和行为</div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" size="large" :loading="loading" @click="handleSave" style="width:100%">
              <el-icon><Check /></el-icon> 保存配置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="info-card" shadow="hover">
        <template #header><span>📋 配置说明</span></template>
        <ul class="help-list">
          <li>修改 API 地址和密钥可切换不同的 AI 服务商</li>
          <li>温度越低回答越严谨，越高越有创意</li>
          <li>配置保存后<span class="highlight">立即生效</span>，无需重启服务</li>
          <li>当前使用 <a href="https://api.deepseek.com/anthropic" target="_blank">DeepSeek Anthropic API</a></li>
        </ul>
      </el-card>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '../api'

const router = useRouter()
const loading = ref(false)
const saved = ref(false)

// 从 localStorage 恢复管理员状态（刷新后保持）
const adminAuth = ref(!!localStorage.getItem('admin_verified'))

const form = reactive({
  AI_API_URL: '',
  AI_API_KEY: '',
  AI_MODEL: '',
  AI_TEMPERATURE: 0.7,
  AI_MAX_TOKENS: 1024,
  AI_SYSTEM_PROMPT: '',
})

onMounted(async () => {
  if (!localStorage.getItem('admin_verified')) {
    router.replace('/')
    return
  }
  await loadConfig()
})

async function loadConfig() {
  try {
    const { data } = await api.get('/admin/config')
    Object.assign(form, data)
  } catch { /* ignore */ }
}

async function handleSave() {
  loading.value = true
  try {
    const payload = { ...form }
    // Temperature and MaxTokens need to be numbers
    payload.AI_TEMPERATURE = parseFloat(payload.AI_TEMPERATURE)
    payload.AI_MAX_TOKENS = parseInt(payload.AI_MAX_TOKENS)
    await api.put('/admin/config', payload)
    saved.value = true
    ElMessage.success('配置已保存，立即生效！')
    setTimeout(() => (saved.value = false), 3000)
  } catch {
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}

function handleLogout() {
  localStorage.removeItem('admin_verified')
  ElMessage.info('已退出管理员模式')
  router.push('/')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f0f2f5;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #e6a23c, #f56c6c);
  padding: 0 24px;
  height: 60px;
  box-shadow: 0 2px 8px rgba(230, 162, 60, .3);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left .el-button { color: #fff; }
.header-left .el-button:hover { background: rgba(255,255,255,.15) !important; }
.header-left h3 { color: #fff; font-size: 16px; margin: 0; }

.header-divider { width: 1px; height: 24px; background: rgba(255,255,255,.3); }

.header-right .el-button { color: rgba(255,255,255,.85); }

.page-main {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  max-width: 700px;
  margin: 0 auto;
}

.config-card, .info-card {
  border-radius: 12px;
  margin-bottom: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.help-list {
  padding-left: 18px;
  color: #606266;
  font-size: 13px;
  line-height: 2;
}

.help-list .highlight {
  color: #e6a23c;
  font-weight: 600;
}

.page-main::-webkit-scrollbar { width: 6px; }
.page-main::-webkit-scrollbar-thumb { background: #c0c4cc; border-radius: 3px; }
</style>
