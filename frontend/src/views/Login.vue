<template>
  <div class="auth-container">
    <div class="auth-bg-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <el-card class="auth-card" shadow="always">
      <template #header>
        <div class="card-header">
          <div class="auth-icon">🤖</div>
          <h2>AI 智能问答系统</h2>
          <p>登录你的账号，开始智能对话</p>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            :prefix-icon="UserIcon"
            size="large"
            clearable
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入密码"
            :prefix-icon="LockIcon"
            size="large"
            @keydown.enter="handleLogin"
          >
            <template #suffix>
              <el-icon class="toggle-pwd" @click="showPassword = !showPassword" :title="showPassword ? '隐藏密码' : '显示密码'">
                <component :is="showPassword ? HideIcon : ViewIcon" />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            :disabled="!form.username || !form.password"
            style="width: 100%"
            @click="handleLogin"
            round
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="auth-footer">
        还没有账号？
        <router-link to="/register">立即注册 →</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User as UserIcon, Lock as LockIcon, Hide as HideIcon, View as ViewIcon } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref(null)
const loading = ref(false)
const showPassword = ref(false)

const form = reactive({ username: '', password: '' })

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const { data } = await api.post('/auth/login', {
      username: form.username,
      password: form.password,
    })
    auth.setToken(data.access_token)
    const { data: userInfo } = await api.get('/auth/me')
    auth.setUser(userInfo)
    ElMessage.success(`欢迎回来，${userInfo.username}！`)
    router.push('/')
  } catch { /* 拦截器处理 */ }
  finally { loading.value = false }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.auth-bg-shapes .shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,.08);
  animation: shapeFloat 20s infinite linear;
}

.shape-1 { width: 400px; height: 400px; top: -100px; right: -80px; }
.shape-2 { width: 300px; height: 300px; bottom: -60px; left: -60px; animation-delay: -7s; }
.shape-3 { width: 200px; height: 200px; top: 50%; left: 50%; animation-delay: -14s; }

@keyframes shapeFloat {
  0%, 100% { transform: translate(0,0) rotate(0deg); }
  33% { transform: translate(30px,-30px) rotate(120deg); }
  66% { transform: translate(-20px,20px) rotate(240deg); }
}

/* 卡片 */
.auth-card {
  width: 420px;
  border-radius: 16px;
  position: relative;
  z-index: 1;
  box-shadow: 0 20px 60px rgba(0,0,0,.15);
  backdrop-filter: blur(10px);
}

.card-header { text-align: center; }

.auth-icon {
  font-size: 48px;
  margin-bottom: 8px;
}

.card-header h2 {
  color: #303133;
  font-size: 22px;
  margin-bottom: 4px;
}

.card-header p {
  color: #909399;
  font-size: 13px;
}

.toggle-pwd { cursor: pointer; color: #909399; }
.toggle-pwd:hover { color: #606266; }

.auth-footer {
  text-align: center;
  color: #909399;
  font-size: 14px;
}
.auth-footer a { color: #667eea; font-weight: 500; }
</style>
