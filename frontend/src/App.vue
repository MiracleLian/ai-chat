<template>
  <router-view v-slot="{ Component }">
    <transition name="fade" mode="out-in">
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<style>
/* ── 全局重置 & 基础 ── */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  overflow: hidden;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
  background-color: #f0f2f5;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ── 页面淡入动画 ── */
.fade-enter-active, .fade-leave-active {
  transition: opacity .2s ease, transform .2s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ── 全局滚动条 ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #c0c4cc; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #909399; }

/* ── 全局链接样式 ── */
a { color: #667eea; text-decoration: none; }
a:hover { text-decoration: underline; }

/* ── Element Plus 细微美化 ── */
.el-button--primary {
  --el-button-bg-color: #667eea;
  --el-button-border-color: #667eea;
  --el-button-hover-bg-color: #7c8ef0;
  --el-button-hover-border-color: #7c8ef0;
  --el-button-active-bg-color: #5a6fd6;
}

.el-tag--primary {
  --el-tag-bg-color: rgba(102,126,234,.1);
  --el-tag-border-color: rgba(102,126,234,.2);
  --el-tag-text-color: #667eea;
}

.el-menu { border-right: none !important; }
</style>
