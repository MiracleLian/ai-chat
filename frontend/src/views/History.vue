<template>
  <div class="history-layout">
    <!-- 顶部导航 -->
    <el-header class="page-header">
      <div class="header-left">
        <el-button text @click="$router.push('/')" class="back-btn">
          <el-icon><ArrowLeft /></el-icon> 返回对话
        </el-button>
        <div class="header-divider"></div>
        <h3>📋 历史对话记录</h3>
        <el-tag size="small" v-if="total > 0">共 {{ total }} 条</el-tag>
      </div>
      <div class="header-right">
        <el-button
          type="danger"
          plain
          :disabled="selectedIds.length === 0"
          @click="confirmBatchDelete"
        >
          <el-icon><Delete /></el-icon> 批量删除 ({{ selectedIds.length }})
        </el-button>
      </div>
    </el-header>

    <!-- 内容区 -->
    <main class="page-main">
      <!-- 骨架屏 -->
      <div v-if="loading" class="history-list">
        <div v-for="n in 5" :key="n" class="skeleton-card">
          <el-skeleton animated>
            <template #template>
              <div style="padding:16px">
                <el-skeleton-item variant="text" style="width:60%;height:20px" />
                <el-skeleton-item variant="text" style="width:90%;height:16px;margin-top:8px" />
                <el-skeleton-item variant="text" style="width:30%;height:14px;margin-top:6px" />
              </div>
            </template>
          </el-skeleton>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty v-else-if="records.length === 0" description="暂无对话记录，去和 AI 聊聊天吧！">
        <el-button type="primary" @click="$router.push('/')">开始对话</el-button>
      </el-empty>

      <!-- 记录列表 -->
      <template v-else>
        <div class="history-list">
          <div v-for="item in records" :key="item.id" class="record-card" :class="{ selected: selectedIds.includes(item.id) }">
            <div class="record-check" @click.stop>
              <el-checkbox
                :model-value="selectedIds.includes(item.id)"
                @change="(val) => toggleSelect(item.id, val)"
              />
            </div>
            <div class="record-body" @click="openDetail(item)">
              <div class="record-question">
                <el-tag type="primary" size="small" effect="plain">Q</el-tag>
                <span class="record-text">{{ truncate(item.question, 80) }}</span>
              </div>
              <div class="record-answer">
                <el-tag type="success" size="small" effect="plain">A</el-tag>
                <span class="record-text">{{ truncate(item.answer || '无回答', 100) }}</span>
              </div>
              <div class="record-meta">
                <span class="record-time">{{ formatDate(item.created_at) }}</span>
                <span class="record-id">#{{ item.id }}</span>
              </div>
            </div>
            <div class="record-actions" @click.stop>
              <el-button circle size="small" @click="openDetail(item)" title="查看详情">
                <el-icon><View /></el-icon>
              </el-button>
              <el-popconfirm
                title="确定删除此条记录？"
                confirm-button-text="删除"
                cancel-button-text="取消"
                @confirm="handleDelete(item.id)"
              >
                <template #reference>
                  <el-button circle size="small" type="danger" title="删除">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination-area" v-if="total > 0">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :page-sizes="[5, 10, 20]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="onPageChange"
            @current-change="onPageChange"
            background
          />
        </div>
      </template>
    </main>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="对话详情"
      width="680px"
      destroy-on-close
      :close-on-click-modal="true"
    >
      <template #header>
        <div class="detail-header">
          <span>📝 对话详情</span>
          <el-tag size="small" type="info">#{{ currentDetail?.id }}</el-tag>
        </div>
      </template>
      <div class="detail-body" v-if="currentDetail">
        <div class="detail-block question-block">
          <div class="detail-label">
            <el-tag type="primary" size="small">问题</el-tag>
            <span class="detail-time">{{ formatDate(currentDetail.created_at) }}</span>
          </div>
          <div class="detail-content">{{ currentDetail.question }}</div>
        </div>
        <div class="detail-block answer-block">
          <div class="detail-label">
            <el-tag type="success" size="small">回答</el-tag>
          </div>
          <div
            class="detail-content markdown-body"
            v-html="renderMarkdown(currentDetail.answer || '无回答')"
          ></div>
        </div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
        <el-popconfirm
          title="确定删除此条记录？"
          @confirm="handleDeleteFromDetail"
        >
          <template #reference>
            <el-button type="danger" plain>删除此记录</el-button>
          </template>
        </el-popconfirm>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import api from '../api'

// 配置 marked
marked.setOptions({ breaks: true, gfm: true })

function renderMarkdown(text) {
  if (!text) return ''
  try { return marked.parse(text) } catch { return text }
}

const records = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const loading = ref(false)
const selectedIds = ref([])
const detailVisible = ref(false)
const currentDetail = ref(null)

onMounted(() => loadHistory())

async function loadHistory() {
  loading.value = true
  try {
    const { data } = await api.get('/chat/history', {
      params: { page: page.value, page_size: pageSize.value },
    })
    records.value = data.records
    total.value = data.total
    if (data.records.length === 0 && page.value > 1) {
      page.value--
      loadHistory()
    }
  } catch { /* 拦截器处理 */ }
  finally { loading.value = false }
}

function onPageChange() {
  selectedIds.value = []
  loadHistory()
}

async function handleDelete(id) {
  try {
    await api.delete(`/chat/${id}`)
    ElMessage.success('删除成功')
    selectedIds.value = selectedIds.value.filter(i => i !== id)
    loadHistory()
  } catch { /* 拦截器处理 */ }
}

async function handleDeleteFromDetail() {
  if (!currentDetail.value) return
  await handleDelete(currentDetail.value.id)
  detailVisible.value = false
}

async function confirmBatchDelete() {
  if (selectedIds.value.length === 0) return
  try {
    await ElMessageBox.confirm(
      `确定删除选中的 ${selectedIds.value.length} 条记录吗？此操作不可撤销。`,
      '批量删除确认',
      { confirmButtonText: '确定删除', cancelButtonText: '取消', type: 'warning' }
    )
    await api.post('/chat/batch-delete', selectedIds.value)
    ElMessage.success(`成功删除 ${selectedIds.value.length} 条记录`)
    selectedIds.value = []
    loadHistory()
  } catch { /* 取消 / 错误 */ }
}

function toggleSelect(id, checked) {
  if (checked) selectedIds.value.push(id)
  else selectedIds.value = selectedIds.value.filter(i => i !== id)
}

function openDetail(item) {
  currentDetail.value = item
  detailVisible.value = true
}

function truncate(text, maxLen) {
  if (!text) return ''
  return text.length > maxLen ? text.slice(0, maxLen) + '...' : text
}

function formatDate(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  const pad = n => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
</script>

<style scoped>
.history-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f0f2f5;
}

/* ── Header ── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.header-right { display: flex; gap: 8px; }

/* ── Main ── */
.page-main {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.history-list {
  max-width: 860px;
  margin: 0 auto;
}

/* 骨架屏 */
.skeleton-card {
  background: #fff;
  border-radius: 10px;
  margin-bottom: 12px;
  overflow: hidden;
}

/* 空状态 */
.el-empty { margin-top: 80px; }

/* 记录卡片 */
.record-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: #fff;
  border-radius: 10px;
  padding: 18px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all .2s;
  border: 2px solid transparent;
  box-shadow: 0 1px 3px rgba(0,0,0,.04);
}

.record-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,.08);
  transform: translateY(-1px);
}

.record-card.selected {
  border-color: #667eea;
  background: #f8f9ff;
}

.record-check {
  padding-top: 2px;
  flex-shrink: 0;
}

.record-body {
  flex: 1;
  min-width: 0;
}

.record-question, .record-answer {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}

.record-text {
  flex: 1;
  color: #303133;
  font-size: 14px;
  line-height: 1.5;
  word-break: break-word;
}

.record-answer .record-text { color: #606266; }

.record-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
}

.record-time { font-size: 12px; color: #909399; }
.record-id { font-size: 11px; color: #c0c4cc; }

.record-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
  padding-top: 2px;
}

/* 分页 */
.pagination-area {
  max-width: 860px;
  margin: 24px auto 0;
  display: flex;
  justify-content: center;
}

/* 详情弹窗 */
.detail-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
}

.detail-body { max-height: 60vh; overflow-y: auto; }

.detail-block {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-block:last-child { border-bottom: none; margin-bottom: 0; }

.detail-label {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.detail-time { font-size: 12px; color: #909399; }

.detail-content {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 14px 16px;
  line-height: 1.7;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-word;
  color: #303133;
}

.answer-block .detail-content { background: #f0f9f0; }

/* Markdown */
.markdown-body :deep(p) { margin: 0 0 8px; }
.markdown-body :deep(p:last-child) { margin-bottom: 0; }
.markdown-body :deep(pre) {
  background: #282c34; color: #abb2bf;
  border-radius: 6px; padding: 12px 16px;
  overflow-x: auto; font-size: 13px; margin: 8px 0;
}
.markdown-body :deep(code) { font-family: 'Cascadia Code','Fira Code','Consolas',monospace; font-size: 13px; }
.markdown-body :deep(p code) { background:#e8e8e8; padding:2px 6px; border-radius:4px; color:#e74c3c; }

/* 滚动条 */
.page-main::-webkit-scrollbar { width: 6px; }
.page-main::-webkit-scrollbar-thumb { background: #c0c4cc; border-radius: 3px; }
</style>
