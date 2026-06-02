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
          <div class="auth-icon">🚀</div>
          <h2>创建新账号</h2>
          <p>注册后即可体验 AI 智能对话</p>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="6-20 位，字母和数字组合"
            :prefix-icon="UserIcon"
            size="large"
            clearable
            maxlength="20"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="8-20 位，需含字母和数字"
            :prefix-icon="LockIcon"
            size="large"
            maxlength="20"
            show-word-limit
          >
            <template #suffix>
              <el-icon class="toggle-pwd" @click="showPassword = !showPassword" :title="showPassword ? '隐藏密码' : '显示密码'">
                <component :is="showPassword ? HideIcon : ViewIcon" />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            :prefix-icon="LockIcon"
            size="large"
            @keydown.enter="handleRegister"
          />
        </el-form-item>

        <el-form-item label="邮箱（选填）" prop="email">
          <el-input
            v-model="form.email"
            placeholder="请输入邮箱地址"
            :prefix-icon="MessageIcon"
            size="large"
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            style="width: 100%"
            @click="handleRegister"
            round
          >
            {{ loading ? '注册中...' : '注 册' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="auth-footer">
        已有账号？
        <router-link to="/login">立即登录 →</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User as UserIcon, Lock as LockIcon, Message as MessageIcon,
  Hide as HideIcon, View as ViewIcon,
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref(null)
const loading = ref(false)
const showPassword = ref(false)

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  email: '',
})

const validateConfirm = (rule, value, callback) => {
  if (value !== form.password) callback(new Error('两次输入的密码不一致'))
  else callback()
}

const validateEmail = (rule, value, callback) => {
  if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) callback(new Error('邮箱格式不正确'))
  else callback()
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 6, max: 20, message: '用户名长度为 6-20 位', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9]+$/, message: '用户名只能包含字母和数字', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, max: 20, message: '密码长度为 8-20 位', trigger: 'blur' },
    { pattern: /^(?=.*[a-zA-Z])(?=.*\d)/, message: '密码需包含字母和数字', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
  email: [{ validator: validateEmail, trigger: 'blur' }],
}

async function handleRegister() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const { data } = await api.post('/auth/register', {
      username: form.username,
      password: form.password,
      email: form.email || undefined,
    })
    auth.setToken(data.access_token)
    const { data: userInfo } = await api.get('/auth/me')
    auth.setUser(userInfo)
    ElMessage.success('注册成功！')
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

.auth-card {
  width: 440px;
  border-radius: 16px;
  position: relative;
  z-index: 1;
  box-shadow: 0 20px 60px rgba(0,0,0,.15);
  max-height: 90vh;
  overflow-y: auto;
  scrollbar-width: thin;
}

.card-header { text-align: center; }
.auth-icon { font-size: 48px; margin-bottom: 8px; }
.card-header h2 { color: #303133; font-size: 22px; margin-bottom: 4px; }
.card-header p { color: #909399; font-size: 13px; }

.toggle-pwd { cursor: pointer; color: #909399; }
.toggle-pwd:hover { color: #606266; }

.auth-footer {
  text-align: center;
  color: #909399;
  font-size: 14px;
}
.auth-footer a { color: #667eea; font-weight: 500; }
</style>
