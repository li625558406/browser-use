<template>
  <div class="task-card" :class="{ disabled: !task.is_enabled, running: isRunning }">
    <div class="card-header">
      <span class="task-name">{{ task.name }}</span>
      <div class="card-meta">
        <el-tag :type="task.is_enabled ? 'success' : 'info'" size="small">
          {{ task.is_enabled ? '启用' : '停用' }}
        </el-tag>
      </div>
    </div>

    <p v-if="task.description" class="task-description">{{ task.description }}</p>

    <div class="card-footer">
      <el-button v-if="!isRunning" size="small" @click="$emit('edit', task)">编辑</el-button>
      <el-button v-if="!isRunning" size="small" @click="$emit('toggle', task.id)">
        {{ task.is_enabled ? '停用' : '启用' }}
      </el-button>
      <el-button v-if="isRunning" size="small" type="warning" @click="$emit('stop', task.id)">停止</el-button>
      <el-button v-else size="small" type="primary" @click="$emit('run', task.id)">运行</el-button>
      <el-button size="small" type="danger" @click="$emit('delete', task.id)">删除</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Task } from '@/api/types'

defineProps<{
  task: Task
  isRunning?: boolean
}>()

defineEmits<{
  edit: [task: Task]
  toggle: [id: number]
  run: [id: number]
  stop: [id: number]
  delete: [id: number]
}>()
</script>

<style scoped>
.task-card {
  border: 1px solid var(--el-border-color);
  border-radius: 8px;
  padding: 16px;
  background: var(--el-bg-color);
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.task-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.task-card.running {
  border-color: var(--el-color-warning);
  box-shadow: 0 0 8px rgba(230, 162, 60, 0.3);
}

.task-card.disabled {
  opacity: 0.6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.task-name {
  font-weight: 600;
  font-size: 15px;
  color: var(--el-text-color-primary);
  flex: 1;
  word-break: break-word;
}

.card-meta {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.task-description {
  color: var(--el-text-color-secondary);
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
}
</style>
