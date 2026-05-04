<template>
  <div class="executions-page">
    <div class="page-header">
      <h2>执行记录</h2>
      <div class="header-actions">
        <el-select v-model="filterStatus" placeholder="筛选状态" clearable style="width: 150px">
          <el-option label="全部" value="" />
          <el-option label="运行中" value="running" />
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
        </el-select>
        <el-select v-model="filterTask" placeholder="筛选任务" clearable style="width: 200px">
          <el-option v-for="task in tasks" :key="task.id" :label="task.name" :value="task.id" />
        </el-select>
        <el-button @click="refreshExecutions">刷新</el-button>
      </div>
    </div>

    <el-table :data="filteredExecutions" style="width: 100%">
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
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="viewDetail(row)">详情</el-button>
          <el-button v-if="row.screenshot_path" size="small" @click="viewScreenshot(row)">截图</el-button>
          <el-button v-if="row.error_message" size="small" type="warning" @click="viewError(row)">错误</el-button>
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

        <div v-if="currentExecution.output" class="output-section">
          <h4>执行输出</h4>
          <pre class="output-content">{{ currentExecution.output }}</pre>
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
import { ElMessage } from 'element-plus'

const executionsStore = useExecutionsStore()
const tasksStore = useTasksStore()

const tasks = computed(() => tasksStore.tasks)

const filterStatus = ref('')
const filterTask = ref<number | null>(null)
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)

const showDetail = ref(false)
const showScreenshot = ref(false)
const currentExecution = ref<any>(null)
const screenshotUrl = ref('')

// 模拟执行记录数据
const mockExecutions = ref([
  {
    id: 1,
    task_id: 1,
    task_name: '每日产品数据抓取',
    status: 'success',
    started_at: '2025-01-04T14:30:00',
    completed_at: '2025-01-04T14:32:15',
    error_message: null,
    screenshot_path: '/screenshots/exec_1.png',
    output: '成功抓取 25 个产品数据...'
  },
  {
    id: 2,
    task_id: 2,
    task_name: '新闻摘要生成',
    status: 'failed',
    started_at: '2025-01-04T12:00:00',
    completed_at: '2025-01-04T12:01:30',
    error_message: 'API 连接超时',
    screenshot_path: null,
    output: '尝试连接 API...'
  },
  {
    id: 3,
    task_id: 1,
    task_name: '每日产品数据抓取',
    status: 'running',
    started_at: '2025-01-04T10:00:00',
    completed_at: null,
    error_message: null,
    screenshot_path: null,
    output: '正在初始化浏览器...'
  }
])

const filteredExecutions = computed(() => {
  let result = mockExecutions.value

  if (filterStatus.value) {
    result = result.filter(e => e.status === filterStatus.value)
  }

  if (filterTask.value) {
    result = result.filter(e => e.task_id === filterTask.value)
  }

  totalCount.value = result.length
  const start = (currentPage.value - 1) * pageSize.value
  return result.slice(start, start + pageSize.value)
})

onMounted(async () => {
  await tasksStore.fetchTasks()
  await executionsStore.fetchExecutions()
})

function statusType(status: string) {
  const types: Record<string, any> = {
    success: 'success',
    failed: 'danger',
    running: 'warning'
  }
  return types[status] || 'info'
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    success: '成功',
    failed: '失败',
    running: '运行中'
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

function refreshExecutions() {
  executionsStore.fetchExecutions()
  ElMessage.success('已刷新')
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
