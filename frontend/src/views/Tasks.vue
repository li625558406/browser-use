<template>
  <div class="tasks-page">
    <div class="page-header">
      <h2>任务管理</h2>
      <el-button type="primary" @click="openCreateDialog">新建任务</el-button>
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

    <el-dialog v-model="showTaskDialog" :title="dialogTitle" width="600px" @closed="handleDialogClosed">
      <TaskForm ref="formRef" v-model="formData" />
      <template #footer>
        <el-button @click="showTaskDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
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
import type { Task, TaskCreate } from '@/api/tasks'

const tasksStore = useTasksStore()
const promptsStore = usePromptsStore()
const llmStore = useLLMStore()

const tasks = computed(() => tasksStore.tasks)
const loading = computed(() => tasksStore.loading)

const showTaskDialog = ref(false)
const isEditMode = ref(false)
const editingTaskId = ref<number | null>(null)
const formData = ref<{
  name: string
  description: string
  target_url: string
  prompt_id?: number
  llm_config_id?: number
  schedule: { type: string; time?: string }
  browser_mode: 'connect' | 'profile'
  profile_name: string
}>({
  name: '',
  description: '',
  target_url: '',
  schedule: { type: 'daily', time: '09:00' },
  browser_mode: 'profile',
  profile_name: 'Default'
})

const dialogTitle = computed(() => isEditMode.value ? '编辑任务' : '新建任务')

onMounted(async () => {
  await Promise.all([
    tasksStore.fetchTasks(),
    promptsStore.fetchPrompts(),
    llmStore.fetchConfigs()
  ])
})

function openCreateDialog() {
  isEditMode.value = false
  editingTaskId.value = null
  resetForm()
  showTaskDialog.value = true
}

function handleEdit(task: Task) {
  isEditMode.value = true
  editingTaskId.value = task.id

  // 填充表单数据
  formData.value = {
    name: task.name,
    description: task.description || '',
    target_url: task.target_url || '',
    prompt_id: task.prompt_id ?? undefined,
    llm_config_id: task.llm_config_id ?? undefined,
    schedule: {
      type: task.schedule_type,
      time: task.schedule_config?.time || '09:00'
    },
    browser_mode: (task.browser_mode as 'connect' | 'profile') || 'profile',
    profile_name: task.profile_name || 'Default'
  }

  showTaskDialog.value = true
}

async function handleSave() {
  try {
    // 清理 undefined 字段，构造 TaskCreate 对象
    const rawFormData = formData.value
    const dataToSubmit: TaskCreate = {
      name: rawFormData.name,
      schedule: rawFormData.schedule,
      browser_mode: rawFormData.browser_mode
    }

    // 添加可选字段
    if (rawFormData.description) dataToSubmit.description = rawFormData.description
    if (rawFormData.target_url) dataToSubmit.target_url = rawFormData.target_url
    if (rawFormData.prompt_id) dataToSubmit.prompt_id = rawFormData.prompt_id
    if (rawFormData.llm_config_id) dataToSubmit.llm_config_id = rawFormData.llm_config_id
    if (rawFormData.profile_name) dataToSubmit.profile_name = rawFormData.profile_name

    if (isEditMode.value && editingTaskId.value) {
      // 更新任务
      await tasksStore.updateTask(editingTaskId.value, dataToSubmit)
      ElMessage.success('任务更新成功')
    } else {
      // 创建任务
      await tasksStore.createTask(dataToSubmit)
      ElMessage.success('任务创建成功')
    }

    showTaskDialog.value = false
    resetForm()
  } catch (e: any) {
    console.error('保存任务失败:', e)
    const errorMsg = e?.response?.data?.message || e?.message || '保存失败'
    ElMessage.error(errorMsg)
  }
}

function handleDialogClosed() {
  resetForm()
}

function resetForm() {
  isEditMode.value = false
  editingTaskId.value = null
  formData.value = {
    name: '',
    description: '',
    target_url: '',
    schedule: { type: 'daily', time: '09:00' },
    browser_mode: 'profile',
    profile_name: 'Default'
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
