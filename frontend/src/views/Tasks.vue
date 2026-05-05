<template>
  <div class="tasks-page">
    <div class="page-header">
      <h2>任务管理</h2>
      <el-button type="primary" @click="openCreateDialog">新建任务</el-button>
    </div>

    <div v-if="tasks.length === 0 && !loading" class="empty-state">
      <el-empty description="暂无任务" />
    </div>
    <div v-else class="task-grid">
      <TaskCard
        v-for="task in tasks"
        :key="task.id"
        :task="task"
        :is-running="runningTaskIds.has(task.id)"
        @edit="handleEdit"
        @toggle="handleToggle"
        @run="handleRun"
        @stop="handleStop"
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
import { tasksApi } from '@/api/tasks'

const tasksStore = useTasksStore()
const promptsStore = usePromptsStore()
const llmStore = useLLMStore()

const tasks = computed(() => tasksStore.tasks)
const loading = computed(() => tasksStore.loading)

const runningTaskIds = ref<Set<number>>(new Set())

const showTaskDialog = ref(false)
const isEditMode = ref(false)
const editingTaskId = ref<number | null>(null)
	const formData = ref<any>({
	  name: '',
	  description: '',
	  target_url: '',
	  requires_login: true,
	  max_items: undefined,
	  prompt_id: undefined,
	  llm_config_id: undefined,
	  schedule: { type: 'daily', time: '09:00' }
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
    max_items: task.max_items ?? undefined,
    requires_login: task.requires_login,
    prompt_id: task.prompt_id ?? undefined,
    llm_config_id: task.llm_config_id ?? undefined,
    schedule: {
      type: task.schedule_type,
      time: task.schedule_config?.time || '09:00'
    }
  }

  showTaskDialog.value = true
}

async function handleSave() {
  try {
    // 清理 undefined 字段，构造 TaskCreate 对象
    const rawFormData = formData.value
    const dataToSubmit: any = {
      name: rawFormData.name,
      schedule: rawFormData.schedule
    }

    // 添加可选字段
    if (rawFormData.description) dataToSubmit.description = rawFormData.description
    if (rawFormData.target_url) dataToSubmit.target_url = rawFormData.target_url
    if (rawFormData.max_items) dataToSubmit.max_items = rawFormData.max_items
    if (rawFormData.requires_login !== undefined) dataToSubmit.requires_login = rawFormData.requires_login
    if (rawFormData.prompt_id) dataToSubmit.prompt_id = rawFormData.prompt_id
    if (rawFormData.llm_config_id) dataToSubmit.llm_config_id = rawFormData.llm_config_id

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
    max_items: undefined,
    requires_login: true,
    schedule: { type: 'daily', time: '09:00' }
  }
}

async function handleToggle(id: number) {
  await tasksStore.toggleTask(id)
  ElMessage.success('任务状态已更新')
}

async function handleRun(id: number) {
  await tasksStore.runTask(id)
  runningTaskIds.value.add(id)
  ElMessage.success('任务已启动，请查看执行记录')
}

async function handleStop(id: number) {
  try {
    await tasksApi.stop(id)
    runningTaskIds.value.delete(id)
    ElMessage.success('任务已停止')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '停止失败')
  }
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

.empty-state {
  padding: 60px 0;
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
</style>
