<template>
  <div class="userinfo-layout">
    <!-- 顶部导航 -->
    <el-header class="page-header">
      <div class="header-left">
        <el-button text @click="$router.push('/')" class="back-btn">
          <el-icon><ArrowLeft /></el-icon> 返回对话
        </el-button>
        <div class="header-divider"></div>
        <h3>👤 个人信息</h3>
      </div>
    </el-header>

    <main class="page-main">
      <el-card class="info-card" shadow="hover" v-loading="loading">
        <!-- 头像区 -->
        <div class="user-avatar-section">
          <el-avatar :size="88" class="user-avatar">
            {{ userInfo.username?.charAt(0)?.toUpperCase() }}
          </el-avatar>
          <div class="user-name-row">
            <h2>{{ userInfo.username }}</h2>
            <el-tag v-if="isAdmin" type="warning" size="small" effect="dark">管理员</el-tag>
          </div>
          <p class="user-email">{{ userInfo.email || '未设置邮箱' }}</p>
        </div>

        <!-- 统计卡片 -->
        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-value">{{ chatCount }}</div>
            <div class="stat-label">对话总数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">#{{ userInfo.id }}</div>
            <div class="stat-label">用户 ID</div>
          </div>
        </div>

        <!-- 详细信息 -->
        <el-descriptions :column="1" border class="info-desc">
          <el-descriptions-item label="用户名" label-align="right">
            {{ userInfo.username }}
          </el-descriptions-item>
          <el-descriptions-item label="用户ID" label-align="right">
            {{ userInfo.id }}
          </el-descriptions-item>
          <el-descriptions-item label="邮箱" label-align="right">
            <template v-if="userInfo.email">
              <el-icon style="margin-right:4px"><Message /></el-icon>
              {{ userInfo.email }}
            </template>
            <span v-else style="color:#c0c4cc">未设置</span>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间" label-align="right">
            <el-icon style="margin-right:4px"><Calendar /></el-icon>
            {{ formatDate(userInfo.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="账号类型" label-align="right">
            <el-tag v-if="isAdmin" type="warning" size="small">管理员</el-tag>
            <el-tag v-else type="info" size="small">普通用户</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="info-actions">
          <el-button type="primary" @click="$router.push('/')">
            <el-icon><ChatDotRound /></el-icon> 返回对话页
          </el-button>
          <el-button type="danger" plain @click="handleLogout">
            <el-icon><SwitchButton /></el-icon> 退出登录
          </el-button>
        </div>
      </el-card>

      <!-- 管理员面板 -->
      <el-card v-if="isAdmin" class="admin-card" shadow="hover">
        <template #header>
          <div class="admin-header">
            <span>🛡️ 管理员面板</span>
            <el-button size="small" @click="goAdmin">用户管理</el-button>
          </div>
        </template>
        <p style="color:#909399;font-size:13px">你可以管理所有用户、查看系统运行状态。</p>
      </el-card>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import api from '../api'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const chatCount = ref(0)
const isAdmin = ref(false)

const userInfo = ref({
  id: '',
  username: '',
  email: '',
  created_at: '',
})

onMounted(() => {
  loadUserInfo()
  loadChatCount()
  checkAdmin()
})

async function loadUserInfo() {
  loading.value = true
  try {
    const { data } = await api.get('/auth/me')
    userInfo.value = data
    auth.setUser(data)
  } catch { /* 拦截器处理 */ }
  finally { loading.value = false }
}

async function loadChatCount() {
  try {
    const { data } = await api.get('/chat/count')
    chatCount.value = data.count
  } catch { /* ignore */ }
}

async function checkAdmin() {
  try {
    const { data } = await api.get('/auth/admin/check')
    isAdmin.value = data.is_admin
  } catch { /* ignore */ }
}

function goAdmin() {
  ElMessage.info('管理员面板开发中...')
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

function formatDate(dt) {
  if (!dt) return '未知'
  return new Date(dt).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}
</script>

<style scoped>
.userinfo-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f0f2f5;
}

.page-header {
  display: flex;
  align-items: center;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 24px;
  height: 60px;
  box-shadow: 0 1px 4px rgba(0,0,0,.04);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-divider {
  width: 1px;
  height: 24px;
  background: #e4e7ed;
}

.header-left h3 {
  color: #303133;
  font-size: 16px;
  margin: 0;
}

.page-main {
  flex: 1;
  overflow-y: auto;
  padding: 40px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.info-card, .admin-card {
  width: 100%;
  max-width: 520px;
  border-radius: 14px;
}

/* 头像区 */
.user-avatar-section {
  text-align: center;
  margin-bottom: 24px;
}

.user-avatar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  font-size: 36px;
  font-weight: 600;
  margin-bottom: 12px;
}

.user-name-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.user-name-row h2 {
  font-size: 22px;
  color: #303133;
}

.user-email {
  color: #909399;
  font-size: 13px;
  margin-top: 4px;
}

/* 统计 */
.stats-row {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  flex: 1;
  text-align: center;
  background: linear-gradient(135deg, #f5f7fa, #e8ecf1);
  border-radius: 10px;
  padding: 16px 12px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.info-desc {
  margin-bottom: 24px;
}

.info-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
}

/* 管理员卡片 */
.admin-card {
  border-color: #e6a23c;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 600;
  color: #303133;
}

/* scrollbar */
.page-main::-webkit-scrollbar { width: 6px; }
.page-main::-webkit-scrollbar-thumb { background: #c0c4cc; border-radius: 3px; }
</style>
