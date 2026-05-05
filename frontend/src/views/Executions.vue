<template>
  <div class="executions-page">
    <div class="page-header">
      <h2>执行记录</h2>
      <div class="header-actions">
        <el-select v-model="filterStatus" placeholder="筛选状态" clearable style="width: 150px" @change="applyFilters">
          <el-option label="全部" value="" />
          <el-option label="等待登录" value="waiting_for_login" />
          <el-option label="运行中" value="running" />
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="已停止" value="stopped" />
        </el-select>
        <el-select v-model="filterTask" placeholder="筛选任务" clearable style="width: 200px" @change="applyFilters">
          <el-option v-for="task in tasks" :key="task.id" :label="task.name" :value="task.id" />
        </el-select>
        <el-button @click="refreshExecutions">刷新</el-button>
      </div>
    </div>

    <el-table :data="displayedExecutions" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="task_name" label="任务名称" width="200" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="started_at" label="开始时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.started_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="completed_at" label="完成时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.completed_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="duration" label="耗时" width="100">
        <template #default="{ row }">
          {{ calculateDuration(row.started_at, row.completed_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.status === 'waiting_for_login'" type="primary" size="small" @click="handleResume(row)">继续执行</el-button>
          <el-button v-if="row.status === 'running'" type="warning" size="small" @click="handleStop(row)">停止</el-button>
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
          <el-button v-if="row.screenshot_path" size="small" @click="viewScreenshot(row)">截图</el-button>
          <el-button v-if="row.error_message" size="small" type="warning" @click="viewError(row)">错误</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="totalCount"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      style="margin-top: 20px; justify-content: flex-end"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />

    <el-dialog v-model="showDetail" title="执行详情" width="800px">
      <div v-if="currentExecution" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="执行ID">{{ currentExecution.id }}</el-descriptions-item>
          <el-descriptions-item label="任务名称">{{ currentExecution.task_name }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(currentExecution.status)">
              {{ statusLabel(currentExecution.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="耗时">
            {{ calculateDuration(currentExecution.started_at, currentExecution.completed_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">{{ formatTime(currentExecution.started_at) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ formatTime(currentExecution.completed_at) }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="currentExecution.error_message" class="error-section">
          <h4>错误信息</h4>
          <el-alert type="error" :closable="false">
            {{ currentExecution.error_message }}
          </el-alert>
        </div>

        <div v-if="currentExecution.log_content" class="output-section">
          <h4>执行输出</h4>
          <pre class="output-content">{{ currentExecution.log_content }}</pre>
        </div>
      </div>
    </el-dialog>

    <el-dialog v-model="showScreenshot" title="截图预览" width="600px">
      <div class="screenshot-content">
        <img v-if="screenshotUrl" :src="screenshotUrl" alt="执行截图" />
        <el-empty v-else description="截图不可用" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useExecutionsStore } from '@/stores/executions'
import { useTasksStore } from '@/stores/tasks'
import { ElMessage, ElMessageBox } from 'element-plus'
import { executionsApi } from '@/api/executions'

const executionsStore = useExecutionsStore()
const tasksStore = useTasksStore()

const tasks = computed(() => tasksStore.tasks)
const executions = computed(() => executionsStore.executions)
const loading = computed(() => executionsStore.loading)

const filterStatus = ref('')
const filterTask = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

const showDetail = ref(false)
const showScreenshot = ref(false)
const currentExecution = ref<any>(null)
const screenshotUrl = ref('')

// 过滤后的执行记录
const filteredExecutions = computed(() => {
  let result = executions.value

  if (filterStatus.value) {
    result = result.filter(e => e.status === filterStatus.value)
  }

  if (filterTask.value) {
    result = result.filter(e => e.task_id === filterTask.value)
  }

  return result
})

// 当前页显示的执行记录
const displayedExecutions = computed(() => {
  const result = filteredExecutions.value
  totalCount.value = result.length
  const start = (currentPage.value - 1) * pageSize.value
  return result.slice(start, start + pageSize.value)
})

onMounted(async () => {
  await tasksStore.fetchTasks()
  await fetchExecutions()
})

async function fetchExecutions() {
  await executionsStore.fetchExecutions()
}

function applyFilters() {
  currentPage.value = 1
}

function handlePageChange(page: number) {
  currentPage.value = page
}

function handleSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
}

function statusType(status: string) {
  const types: Record<string, any> = {
    success: 'success',
    failed: 'danger',
    running: 'warning',
    waiting_for_login: 'info',
    stopped: 'warning'
  }
  return types[status] || 'info'
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    success: '成功',
    failed: '失败',
    running: '运行中',
    waiting_for_login: '等待登录',
    stopped: '已停止'
  }
  return labels[status] || status
}

function formatTime(time: string | null) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

function calculateDuration(start: string, end: string | null) {
  if (!start) return '-'
  const startTime = new Date(start).getTime()
  const endTime = end ? new Date(end).getTime() : Date.now()
  const seconds = Math.floor((endTime - startTime) / 1000)
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  return `${minutes}分${seconds % 60}秒`
}

function viewDetail(execution: any) {
  currentExecution.value = execution
  showDetail.value = true
}

function viewScreenshot(execution: any) {
  screenshotUrl.value = execution.screenshot_path || ''
  showScreenshot.value = true
}

function viewError(execution: any) {
  ElMessage.error(execution.error_message)
}

async function handleDelete(execution: any) {
  await ElMessageBox.confirm('确定删除此执行记录？', '确认', { type: 'warning' })
  await executionsStore.deleteExecution(execution.id)
  ElMessage.success('执行记录已删除')
  await fetchExecutions()
}

function refreshExecutions() {
  fetchExecutions()
  ElMessage.success('已刷新')
}

async function handleStop(execution: any) {
  try {
    await ElMessageBox.confirm('确定停止此执行？', '确认', { type: 'warning' })
    await executionsApi.stop(execution.task_id)
    ElMessage.success('任务已停止')
    await fetchExecutions()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e?.response?.data?.message || '停止失败')
    }
  }
}

async function handleResume(execution: any) {
  try {
    const loading = ElMessage.info({
      message: '正在继续执行任务...',
      duration: 0,
    })

    await executionsApi.resume(execution.task_id)

    loading.close()
    ElMessage.success('任务已继续执行')

    // 刷新执行记录
    await fetchExecutions()
  } catch (e: any) {
    const errorMsg = e?.response?.data?.message || e?.message || '继续执行失败'
    ElMessage.error(errorMsg)
  }
}
</script>

<style scoped>
.executions-page {
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

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.error-section,
.output-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.error-section h4,
.output-section h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}

.output-content {
  margin: 0;
  padding: 12px;
  background: var(--bg-color);
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.5;
  max-height: 300px;
  overflow-y: auto;
}

.screenshot-content {
  text-align: center;
}

.screenshot-content img {
  max-width: 100%;
  border-radius: 4px;
}
</style>
