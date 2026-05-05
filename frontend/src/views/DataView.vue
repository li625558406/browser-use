<template>
  <div class="data-page">
    <div class="page-header">
      <h2>数据查看</h2>
      <div class="header-actions">
        <el-select v-model="selectedTask" placeholder="筛选任务" clearable style="width: 200px" @change="loadExportFiles">
          <el-option v-for="task in tasks" :key="task.id" :label="task.name" :value="task.id" />
        </el-select>
        <el-button @click="loadExportFiles">刷新</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="导出文件" name="files">
        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="3" animated />
        </div>
        <div v-else-if="exportFiles.length === 0" class="empty-state">
          <el-empty description="暂无导出文件">
            <el-button type="primary" @click="$router.push('/executions')">查看执行记录</el-button>
          </el-empty>
        </div>
        <div v-else class="file-list">
          <el-card v-for="file in exportFiles" :key="file.name" class="file-card">
            <div class="file-info">
              <el-icon class="file-icon"><Document /></el-icon>
              <div class="file-details">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">
                  <span>{{ file.size }}</span>
                  <span>{{ formatDate(file.date) }}</span>
                </div>
              </div>
            </div>
            <template #footer>
              <div class="file-actions">
                <el-button size="small" @click="openPreview(file)">预览</el-button>
                <el-button size="small" type="primary" @click="downloadFile(file)">下载</el-button>
              </div>
            </template>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="执行记录数据" name="executions">
        <div class="executions-filter">
          <el-select v-model="executionStatus" placeholder="筛选状态" clearable style="width: 150px" @change="loadExecutions">
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
            <el-option label="运行中" value="running" />
          </el-select>
        </div>
        <div v-if="loadingExecutions" class="loading-state">
          <el-skeleton :rows="3" animated />
        </div>
        <div v-else-if="filteredExecutions.length === 0" class="empty-state">
          <el-empty description="暂无执行记录" />
        </div>
        <div v-else class="execution-list">
          <el-card v-for="execution in filteredExecutions" :key="execution.id" class="execution-card">
            <div class="execution-header">
              <span class="execution-title">{{ execution.task_name }}</span>
              <el-tag :type="getStatusType(execution.status)" size="small">
                {{ getStatusLabel(execution.status) }}
              </el-tag>
            </div>
            <div class="execution-meta">
              <span>{{ formatTime(execution.started_at) }}</span>
              <span v-if="execution.completed_at && execution.started_at">耗时 {{ calculateDuration(execution.started_at!, execution.completed_at) }}</span>
            </div>
            <template #footer>
              <div class="execution-actions">
                <el-button v-if="execution.log_content" size="small" @click="viewExecutionLog(execution)">查看日志</el-button>
                <el-button v-if="execution.status === 'success'" size="small" type="primary" @click="exportExecution(execution.id)">导出</el-button>
              </div>
            </template>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 文件预览对话框 -->
    <el-dialog v-model="showPreview" :title="previewFile?.name" width="800px">
      <div v-if="loadingPreview" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else class="preview-content">
        <pre v-if="previewContent">{{ previewContent }}</pre>
        <el-empty v-else description="无法加载预览" />
      </div>
      <template #footer>
        <el-button @click="showPreview = false">关闭</el-button>
        <el-button type="primary" @click="downloadFile(previewFile!)">下载</el-button>
      </template>
    </el-dialog>

    <!-- 执行日志对话框 -->
    <el-dialog v-model="showLogDialog" :title="`执行日志 - ${currentExecution?.task_name}`" width="900px">
      <div class="log-content">
        <pre v-if="currentExecution?.log_content">{{ currentExecution.log_content }}</pre>
        <el-empty v-else description="无日志内容" />
      </div>
      <template #footer>
        <el-button @click="showLogDialog = false">关闭</el-button>
        <el-button v-if="currentExecution" type="primary" @click="exportExecution(currentExecution.id)">导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTasksStore } from '@/stores/tasks'
import { executionsApi, type ExportFile } from '@/api/executions'
import type { TaskExecution } from '@/api/types'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'

const tasksStore = useTasksStore()
const tasks = computed(() => tasksStore.tasks)

const activeTab = ref('files')
const selectedTask = ref<number | null>(null)
const executionStatus = ref<string>('success')
const loading = ref(false)
const loadingExecutions = ref(false)
const loadingPreview = ref(false)

const exportFiles = ref<ExportFile[]>([])
const executions = ref<TaskExecution[]>([])
const showPreview = ref(false)
const previewFile = ref<ExportFile | null>(null)
const previewContent = ref('')
const showLogDialog = ref(false)
const currentExecution = ref<TaskExecution | null>(null)

// 按状态筛选执行记录
const filteredExecutions = computed(() => {
  if (!executionStatus.value) return executions.value
  return executions.value.filter(e => e.status === executionStatus.value)
})

onMounted(async () => {
  await tasksStore.fetchTasks()
  await loadExportFiles()
  await loadExecutions()
})

async function loadExportFiles() {
  loading.value = true
  try {
    exportFiles.value = await executionsApi.listExports()
  } catch (e: any) {
    ElMessage.error('加载导出文件失败: ' + (e?.response?.data?.message || e?.message))
  } finally {
    loading.value = false
  }
}

async function loadExecutions() {
  loadingExecutions.value = true
  try {
    const response = await executionsApi.list(selectedTask.value || undefined, undefined)
    executions.value = response
  } catch (e: any) {
    ElMessage.error('加载执行记录失败')
  } finally {
    loadingExecutions.value = false
  }
}

async function openPreview(file: ExportFile) {
  previewFile.value = file
  loadingPreview.value = true
  showPreview.value = true
  previewContent.value = ''

  try {
    // 通过 fetch 读取文件内容
    const response = await fetch(`/api/executions/exports/${file.name}`)
    if (response.ok) {
      previewContent.value = await response.text()
    } else {
      ElMessage.error('无法加载文件预览')
    }
  } catch (e) {
    ElMessage.error('预览加载失败')
  } finally {
    loadingPreview.value = false
  }
}

function downloadFile(file: ExportFile) {
  executionsApi.downloadExport(file.name)
  ElMessage.success(`开始下载 ${file.name}`)
}

function exportExecution(id: number) {
  executionsApi.export(id)
  ElMessage.success('开始导出')
}

function viewExecutionLog(execution: TaskExecution) {
  currentExecution.value = execution
  showLogDialog.value = true
}

function formatDate(timestamp: number) {
  return new Date(timestamp * 1000).toLocaleString('zh-CN')
}

function formatTime(time: string | null) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

function calculateDuration(start: string, end: string | null) {
  if (!start || !end) return '-'
  const startTime = new Date(start).getTime()
  const endTime = new Date(end).getTime()
  const seconds = Math.floor((endTime - startTime) / 1000)
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  return `${minutes}分${seconds % 60}秒`
}

function getStatusType(status: string) {
  const types: Record<string, any> = {
    success: 'success',
    failed: 'danger',
    running: 'warning',
    waiting_for_login: 'info',
    stopped: 'warning'
  }
  return types[status] || 'info'
}

function getStatusLabel(status: string) {
  const labels: Record<string, string> = {
    success: '成功',
    failed: '失败',
    running: '运行中',
    waiting_for_login: '等待登录',
    stopped: '已停止'
  }
  return labels[status] || status
}
</script>

<style scoped>
.data-page {
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

.loading-state,
.empty-state {
  padding: 60px 0;
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-card {
  margin-bottom: 0;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  font-size: 32px;
  color: var(--el-color-primary);
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 500;
  margin-bottom: 4px;
  word-break: break-all;
}

.file-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.file-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.executions-filter {
  margin-bottom: 16px;
}

.execution-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.execution-card {
  margin-bottom: 0;
}

.execution-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.execution-title {
  font-weight: 600;
  font-size: 15px;
}

.execution-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.execution-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.preview-content,
.log-content {
  max-height: 500px;
  overflow-y: auto;
}

.preview-content pre,
.log-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
}
</style>
