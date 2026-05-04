<template>
  <aside class="app-sidebar">
    <nav class="sidebar-nav">
      <router-link to="/tasks" class="nav-item" active-class="active">
        <el-icon><List /></el-icon>
        <span>任务管理</span>
      </router-link>
      <router-link to="/prompts" class="nav-item" active-class="active">
        <el-icon><Document /></el-icon>
        <span>Prompt 管理</span>
      </router-link>
      <router-link to="/llm" class="nav-item" active-class="active">
        <el-icon><Setting /></el-icon>
        <span>LLM 配置</span>
      </router-link>
      <router-link to="/data" class="nav-item" active-class="active">
        <el-icon><FolderOpened /></el-icon>
        <span>数据查看</span>
      </router-link>
      <router-link to="/executions" class="nav-item" active-class="active">
        <el-icon><Clock /></el-icon>
        <span>执行记录</span>
      </router-link>
      <router-link to="/settings" class="nav-item" active-class="active">
        <el-icon><Tools /></el-icon>
        <span>设置</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { List, Document, Setting, FolderOpened, Clock, Tools } from '@element-plus/icons-vue'
</script>

<style scoped>
.app-sidebar {
  width: 200px;
  height: 100%;
  background: var(--bg-color-page);
  border-right: 1px solid var(--border-color);
}

.sidebar-nav {
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: var(--text-color-regular);
  text-decoration: none;
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--bg-color);
  color: var(--color-primary);
}

.nav-item.active {
  background: var(--color-primary);
  color: white;
}
</style>
