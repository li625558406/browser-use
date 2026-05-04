<template>
  <el-card class="task-card" :class="{ disabled: !task.is_enabled }">
    <template #header>
      <div class="card-header">
        <span class="task-name">{{ task.name }}</span>
        <el-tag :type="task.is_enabled ? 'success' : 'info'" size="small">
          {{ task.is_enabled ? '启用' : '停用' }}
        </el-tag>
      </div>
    </template>

    <div class="task-info">
      <p v-if="task.description" class="task-description">{{ task.description }}</p>
      <div class="task-meta">
        <el-tag size="small">{{ scheduleText }}</el-tag>
        <el-tag size="small" type="info">{{ browserModeText }}</el-tag>
      </div>
    </div>

    <template #footer>
      <div class="card-actions">
        <el-button size="small" @click="$emit('edit', task)">编辑</el-button>
        <el-button size="small" @click="$emit('toggle', task.id)">
          {{ task.is_enabled ? '停用' : '启用' }}
        </el-button>
        <el-button size="small" type="primary" @click="$emit('run', task.id)">运行</el-button>
        <el-button size="small" type="danger" @click="$emit('delete', task.id)">删除</el-button>
      </div>
    </template>
  </el-card>
</template>

<script setup lang="ts">
import type { Task } from '@/api/types'

const props = defineProps<{
  task: Task
}>()

defineEmits<{
  edit: [task: Task]
  toggle: [id: number]
  run: [id: number]
  delete: [id: number]
}>()

const scheduleText = computed(() => {
  const type = props.task.schedule_type
  const map: Record<string, string> = {
    once: '一次性',
    daily: '每天',
    weekly: '每周',
    custom: '自定义'
  }
  return map[type] || type
})

const browserModeText = computed(() => {
  return props.task.browser_mode === 'connect' ? 'CDP连接' : 'Chrome配置'
})
</script>

<style scoped>
.task-card {
  margin-bottom: 16px;
}

.task-card.disabled {
  opacity: 0.6;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-name {
  font-weight: 600;
  font-size: 16px;
}

.task-description {
  color: var(--text-color-secondary);
  margin: 0 0 12px 0;
}

.task-meta {
  display: flex;
  gap: 8px;
}

.card-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
