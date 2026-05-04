<template>
  <div class="settings-page">
    <h2>设置</h2>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="浏览器配置" name="browser">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <span>浏览器设置</span>
            </div>
          </template>

          <el-form label-width="150px">
            <el-form-item label="CDP 端口">
              <el-input-number v-model="settings.cdpPort" :min="1024" :max="65535" />
              <span class="form-tip">Chrome 远程调试端口</span>
            </el-form-item>

            <el-form-item label="可用配置">
              <div class="profile-list">
                <div v-for="profile in availableProfiles" :key="profile.name" class="profile-item">
                  <el-icon><User /></el-icon>
                  <span>{{ profile.name }}</span>
                  <el-tag size="small">{{ profile.path }}</el-tag>
                </div>
                <el-button @click="refreshProfiles" :loading="loadingProfiles">刷新列表</el-button>
              </div>
            </el-form-item>

            <el-form-item label="连接状态">
              <div class="connection-status">
                <el-tag :type="isConnected ? 'success' : 'danger'">
                  {{ isConnected ? '已连接' : '未连接' }}
                </el-tag>
                <el-button @click="testConnection" :loading="testingConnection">测试连接</el-button>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="调度设置" name="scheduler">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <span>任务调度</span>
            </div>
          </template>

          <el-form label-width="150px">
            <el-form-item label="最大并发数">
              <el-input-number v-model="settings.maxWorkers" :min="1" :max="10" />
              <span class="form-tip">同时执行的最大任务数</span>
            </el-form-item>

            <el-form-item label="默认超时">
              <el-input-number v-model="settings.defaultTimeout" :min="60" :max="3600" />
              <span class="form-tip">任务执行超时时间（秒）</span>
            </el-form-item>

            <el-form-item label="失败重试">
              <el-input-number v-model="settings.maxRetries" :min="0" :max="5" />
              <span class="form-tip">任务失败后的重试次数</span>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="系统设置" name="system">
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <span>系统配置</span>
            </div>
          </template>

          <el-form label-width="150px">
            <el-form-item label="日志级别">
              <el-select v-model="settings.logLevel">
                <el-option label="DEBUG" value="DEBUG" />
                <el-option label="INFO" value="INFO" />
                <el-option label="WARNING" value="WARNING" />
                <el-option label="ERROR" value="ERROR" />
              </el-select>
            </el-form-item>

            <el-form-item label="数据导出目录">
              <el-input v-model="settings.exportPath" placeholder="/app/data/exports" readonly />
              <span class="form-tip">导出文件的保存路径</span>
            </el-form-item>

            <el-form-item label="数据库">
              <div class="database-info">
                <el-tag>SQLite</el-tag>
                <span>{{ settings.databasePath }}</span>
              </div>
            </el-form-item>

            <el-form-item label="版本信息">
              <div class="version-info">
                <div>WebUI 版本: <span class="version">v1.0.0</span></div>
                <div>browser-use 版本: <span class="version">latest</span></div>
              </div>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="关于" name="about">
        <el-card class="settings-card">
          <div class="about-content">
            <h1>Browser-Use WebUI</h1>
            <p class="version">v1.0.0</p>
            <p class="description">
              基于 browser-use 的 Web 界面，支持定时任务、多 LLM 配置、浏览器自动化等功能。
            </p>

            <div class="links">
              <el-button type="primary" @click="openGitHub">
                <el-icon><Link /></el-icon>
                GitHub 仓库
              </el-button>
              <el-button @click="openDocs">
                <el-icon><Document /></el-icon>
                使用文档
              </el-button>
            </div>

            <el-divider />

            <div class="tech-stack">
              <h3>技术栈</h3>
              <div class="stack-list">
                <div class="stack-item">
                  <span class="stack-label">后端:</span>
                  <span class="stack-value">FastAPI + SQLAlchemy + APScheduler</span>
                </div>
                <div class="stack-item">
                  <span class="stack-label">前端:</span>
                  <span class="stack-value">Vue 3 + Vite + Element Plus + Pinia</span>
                </div>
                <div class="stack-item">
                  <span class="stack-label">数据库:</span>
                  <span class="stack-value">SQLite (可升级至 PostgreSQL)</span>
                </div>
                <div class="stack-item">
                  <span class="stack-label">浏览器:</span>
                  <span class="stack-value">Chrome/Chromium + CDP</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <div class="settings-actions">
      <el-button @click="resetSettings">重置默认</el-button>
      <el-button type="primary" @click="saveSettings">保存设置</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { browserApi } from '@/api/browser'
import { ElMessage } from 'element-plus'
import { User, Link, Document } from '@element-plus/icons-vue'

const activeTab = ref('browser')

const settings = ref({
  cdpPort: 9242,
  maxWorkers: 3,
  defaultTimeout: 300,
  maxRetries: 2,
  logLevel: 'INFO',
  exportPath: '/app/data/exports',
  databasePath: '/app/data/database.db'
})

const availableProfiles = ref([
  { name: 'Default', path: 'C:\\Users\\...\\AppData\\Local\\Google\\Chrome\\User Data' },
  { name: 'Profile 1', path: 'C:\\Users\\...\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1' }
])

const isConnected = ref(false)
const loadingProfiles = ref(false)
const testingConnection = ref(false)

onMounted(async () => {
  await checkBrowserStatus()
})

async function checkBrowserStatus() {
  try {
    const status = await browserApi.getStatus()
    isConnected.value = status.is_connected
    availableProfiles.value = status.profiles
  } catch (e) {
    console.error('Failed to get browser status:', e)
  }
}

async function refreshProfiles() {
  loadingProfiles.value = true
  await checkBrowserStatus()
  loadingProfiles.value = false
  ElMessage.success('已刷新配置列表')
}

async function testConnection() {
  testingConnection.value = true
  try {
    const result = await browserApi.testConnection(settings.value.cdpPort)
    isConnected.value = result.success
    if (result.success) {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error(result.message || '连接测试失败')
    }
  } catch (e) {
    ElMessage.error('连接测试失败')
  } finally {
    testingConnection.value = false
  }
}

function saveSettings() {
  localStorage.setItem('webui-settings', JSON.stringify(settings.value))
  ElMessage.success('设置已保存')
}

function resetSettings() {
  settings.value = {
    cdpPort: 9242,
    maxWorkers: 3,
    defaultTimeout: 300,
    maxRetries: 2,
    logLevel: 'INFO',
    exportPath: '/app/data/exports',
    databasePath: '/app/data/database.db'
  }
  ElMessage.success('已重置为默认设置')
}

function openGitHub() {
  window.open('https://github.com/browser-use/browser-use', '_blank')
}

function openDocs() {
  window.open('/WEBUI_README.md', '_blank')
}
</script>

<style scoped>
.settings-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.settings-page h2 {
  margin: 0;
}

.settings-card {
  margin-bottom: 20px;
}

.card-header {
  font-weight: 600;
}

.form-tip {
  margin-left: 12px;
  font-size: 12px;
  color: var(--text-color-secondary);
}

.profile-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.profile-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-color);
  border-radius: 4px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.database-info,
.version-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.version {
  font-family: monospace;
  color: var(--color-primary);
}

.about-content {
  text-align: center;
  padding: 20px;
}

.about-content h1 {
  margin: 0 0 8px 0;
}

.about-content .version {
  font-size: 18px;
  color: var(--text-color-secondary);
  margin: 0 0 20px 0;
}

.about-content .description {
  color: var(--text-color-regular);
  margin-bottom: 30px;
}

.links {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 30px;
}

.tech-stack {
  text-align: left;
}

.tech-stack h3 {
  margin: 0 0 16px 0;
}

.stack-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stack-item {
  display: flex;
  gap: 12px;
}

.stack-label {
  font-weight: 500;
  min-width: 60px;
}

.stack-value {
  color: var(--text-color-secondary);
}

.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}
</style>
