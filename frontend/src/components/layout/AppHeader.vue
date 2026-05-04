<template>
  <header class="app-header">
    <div class="header-left">
      <h1 class="app-title">Browser-Use WebUI</h1>
    </div>
    <div class="header-right">
      <el-button @click="openGitHub" link>
        <el-icon><Link /></el-icon>
        GitHub
      </el-button>
    </div>
  </header>
</template>

<script setup lang="ts">
import { Link } from '@element-plus/icons-vue'

function openGitHub() {
  window.open('https://github.com/browser-use/browser-use', '_blank')
}
</script>

<style scoped>
.app-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: var(--bg-color-page);
  border-bottom: 1px solid var(--border-color);
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-color-primary);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
</style>
