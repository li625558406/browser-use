<template>
  <div class="data-page">
    <div class="page-header">
      <h2>数据查看</h2>
      <div class="header-actions">
        <el-select v-model="selectedTask" placeholder="筛选任务" clearable style="width: 200px">
          <el-option v-for="task in tasks" :key="task.id" :label="task.name" :value="task.id" />
        </el-select>
        <el-button @click="refreshData">刷新</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="导出文件" name="files">
        <div v-if="exportFiles.length === 0" class="empty-state">
          <el-empty description="暂无导出文件" />
        </div>
        <div v-else class="file-list">
          <el-card v-for="file in exportFiles" :key="file.name" class="file-card">
            <div class="file-info">
              <el-icon class="file-icon"><Document /></el-icon>
              <div class="file-details">
                <div class="file-name">{{ file.name }}</div>
                <div class="file-meta">
                  <span>{{ file.size }}</span>
                  <span>{{ file.date }}</span>
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

      <el-tab-pane label="分类浏览" name="category">
        <div class="category-list">
          <div v-for="category in dataCategories" :key="category.name" class="category-item">
            <div class="category-header" @click="toggleCategory(category.name)">
              <el-icon class="category-icon"><Folder /></el-icon>
              <span class="category-name">{{ category.name }}</span>
              <el-badge :value="category.count" class="category-badge" />
            </div>
            <div v-show="expandedCategories.has(category.name)" class="category-files">
              <div v-for="file in category.files" :key="file.name" class="category-file" @click="openPreview(file)">
                <el-icon><Document /></el-icon>
                <span>{{ file.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showPreview" :title="previewFile?.name" width="800px">
      <div class="preview-content">
        <pre v-if="previewContent">{{ previewContent }}</pre>
        <el-empty v-else description="无法加载预览" />
      </div>
      <template #footer>
        <el-button @click="showPreview = false">关闭</el-button>
        <el-button type="primary" @click="downloadFile(previewFile!)">下载</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTasksStore } from '@/stores/tasks'
import { ElMessage } from 'element-plus'
import { Document, Folder } from '@element-plus/icons-vue'

const tasksStore = useTasksStore()
const tasks = computed(() => tasksStore.tasks)

const activeTab = ref('files')
const selectedTask = ref<number | null>(null)
const expandedCategories = ref<Set<string>>(new Set())
const showPreview = ref(false)
const previewFile = ref<any>(null)
const previewContent = ref('')

// 模拟导出文件数据
const exportFiles = ref([
  { name: 'product_data_20250104.md', size: '12.5 KB', date: '2025-01-04 14:30' },
  { name: 'news_summary_20250104.md', size: '8.2 KB', date: '2025-01-04 12:15' },
  { name: 'scraped_data_20250103.md', size: '45.6 KB', date: '2025-01-03 18:45' }
])

const dataCategories = ref([
  {
    name: '电商数据',
    count: 15,
    files: [
      { name: 'product_data_20250104.md' },
      { name: 'product_data_20250103.md' }
    ]
  },
  {
    name: '新闻摘要',
    count: 8,
    files: [
      { name: 'news_summary_20250104.md' },
      { name: 'news_summary_20250103.md' }
    ]
  },
  {
    name: '通用数据',
    count: 22,
    files: [
      { name: 'scraped_data_20250103.md' }
    ]
  }
])

onMounted(async () => {
  await tasksStore.fetchTasks()
})

function toggleCategory(name: string) {
  if (expandedCategories.value.has(name)) {
    expandedCategories.value.delete(name)
  } else {
    expandedCategories.value.add(name)
  }
}

function openPreview(file: any) {
  previewFile.value = file
  previewContent.value = `# ${file.name}\n\n这是文件预览内容...\n\n实际使用时，这里会从服务器加载文件内容。`
  showPreview.value = true
}

function downloadFile(file: any) {
  ElMessage.success(`下载 ${file.name}`)
  // 实际下载逻辑
}

function refreshData() {
  ElMessage.success('数据已刷新')
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
  color: var(--color-primary);
}

.file-details {
  flex: 1;
}

.file-name {
  font-weight: 500;
  margin-bottom: 4px;
}

.file-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-color-secondary);
}

.file-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.category-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-item {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  overflow: hidden;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-color);
  cursor: pointer;
  transition: background 0.2s;
}

.category-header:hover {
  background: var(--border-color-lighter);
}

.category-icon {
  font-size: 20px;
  color: var(--color-warning);
}

.category-name {
  flex: 1;
  font-weight: 500;
}

.category-files {
  border-top: 1px solid var(--border-color);
  background: white;
}

.category-file {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px 10px 48px;
  cursor: pointer;
  transition: background 0.2s;
}

.category-file:hover {
  background: var(--bg-color);
}

.preview-content {
  max-height: 500px;
  overflow-y: auto;
}

.preview-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: monospace;
  font-size: 14px;
  line-height: 1.6;
}
</style>
