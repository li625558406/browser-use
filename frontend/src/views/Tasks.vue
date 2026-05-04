<template>
  <div class="tasks-page">
    <div class="page-header">
      <h2>任务管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">新建任务</el-button>
    </div>

    <div class="task-list">
      <el-empty v-if="tasks.length === 0 && !loading" description="暂无任务" />
      <TaskCard
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        @edit="handleEdit"
        @toggle="handleToggle"
        @run="handleRun"
        @delete="handleDelete"
      />
    </div>

    <el-dialog v-model="showCreateDialog" title="新建任务" width="600px">
      <TaskForm ref="formRef" v-model="formData" />
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTasksStore } from '@/stores/tasks'
import { usePromptsStore } from '@/stores/prompts'
import { useLLMStore } from '@/stores/llm'
import { ElMessage, ElMessageBox } from 'element-plus'
import TaskCard from '@/components/tasks/TaskCard.vue'
import TaskForm from '@/components/tasks/TaskForm.vue'
import type { Task } from '@/api/types'

const tasksStore = useTasksStore()
const promptsStore = usePromptsStore()
const llmStore = useLLMStore()

const tasks = computed(() => tasksStore.tasks)
const loading = computed(() => tasksStore.loading)

const showCreateDialog = ref(false)
const formData = ref({
  name: '',
  description: '',
  target_url: '',
  prompt_id: undefined,
  llm_config_id: undefined,
  schedule: { type: 'daily', time: '09:00' },
  browser_mode: 'profile' as const,
  profile_name: 'Default'
})

onMounted(async () => {
  await Promise.all([
    tasksStore.fetchTasks(),
    promptsStore.fetchPrompts(),
    llmStore.fetchConfigs()
  ])
})

async function handleCreate() {
  try {
    await tasksStore.createTask(formData.value)
    ElMessage.success('任务创建成功')
    showCreateDialog.value = false
  } catch (e) {
    ElMessage.error('创建失败')
  }
}

async function handleToggle(id: number) {
  await tasksStore.toggleTask(id)
  ElMessage.success('任务状态已更新')
}

async function handleRun(id: number) {
  await tasksStore.runTask(id)
  ElMessage.success('任务已启动')
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定删除此任务？', '确认', { type: 'warning' })
  await tasksStore.deleteTask(id)
  ElMessage.success('任务已删除')
}

function handleEdit(task: Task) {
  // TODO: Implement edit dialog
  ElMessage.info('编辑功能开发中')
}
</script>

<style scoped>
.tasks-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
}

.task-list {
  display: flex;
  flex-direction: column;
}
</style>
