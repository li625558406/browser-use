<template>
  <div class="llm-page">
    <div class="page-header">
      <h2>LLM 配置</h2>
      <el-button type="primary" @click="openCreateDialog">新建配置</el-button>
    </div>

    <div class="config-grid">
      <div
        v-for="config in configs"
        :key="config.id"
        class="config-card"
        :class="{ default: config.is_default }"
        @click="handleView(config)"
      >
        <div class="card-header">
          <span class="config-name">{{ config.name }}</span>
          <div class="card-meta">
            <el-tag v-if="config.is_default" type="success" size="small">默认</el-tag>
            <el-tag size="small">{{ providerLabel(config.provider) }}</el-tag>
          </div>
        </div>
        <div class="config-info">
          <div class="info-item">
            <span class="label">模型</span>
            <span class="value">{{ config.model }}</span>
          </div>
          <div class="info-item">
            <span class="label">温度</span>
            <span class="value">{{ config.temperature }}</span>
          </div>
        </div>
        <div class="card-footer">
          <el-button size="small" @click.stop="handleEdit(config)">编辑</el-button>
          <el-button size="small" @click.stop="handleTest(config.id)">测试</el-button>
          <el-dropdown v-if="!config.is_default" @click.stop>
            <el-button size="small" type="danger">
              更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="handleSetDefault(config.id)">设为默认</el-dropdown-item>
                <el-dropdown-item @click="handleDelete(config.id)">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </div>

    <!-- 查看/编辑对话框 -->
    <el-dialog v-model="showDialog" :title="dialogTitle" width="700px" @closed="resetForm">
      <el-form v-if="!isViewMode" :model="formData" label-width="120px">
        <el-form-item label="配置名称" required>
          <el-input v-model="formData.name" placeholder="例如: DeepSeek Chat" />
        </el-form-item>
        <el-form-item label="提供商" required>
          <el-select v-model="formData.provider" placeholder="选择提供商" style="width: 100%">
            <el-option label="DeepSeek" value="deepseek" />
            <el-option label="OpenAI" value="openai" />
            <el-option label="Anthropic" value="anthropic" />
            <el-option label="Ollama" value="ollama" />
            <el-option label="OpenAI兼容" value="openai_compatible" />
          </el-select>
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="formData.api_key" type="password" placeholder="输入 API Key" show-password />
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="formData.base_url" placeholder="自定义 API 地址（可选）">
            <template #append>
              <el-button @click="setDefaultUrl">使用默认</el-button>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="模型名称" required>
          <el-input v-model="formData.model" placeholder="例如: deepseek-chat" />
        </el-form-item>
        <el-form-item label="Temperature">
          <el-slider v-model="formData.temperature" :min="0" :max="2" :step="0.1" show-input />
        </el-form-item>
        <el-form-item label="Max Tokens">
          <el-input-number v-model="formData.max_tokens" :min="1" :max="128000" style="width: 100%" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="formData.is_default" />
        </el-form-item>
      </el-form>
      <div v-else class="view-mode">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="配置名称">{{ currentConfig?.name }}</el-descriptions-item>
          <el-descriptions-item label="提供商">
            <el-tag size="small">{{ providerLabel(currentConfig?.provider || '') }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="模型">{{ currentConfig?.model }}</el-descriptions-item>
          <el-descriptions-item label="Temperature">{{ currentConfig?.temperature }}</el-descriptions-item>
          <el-descriptions-item label="Max Tokens">{{ currentConfig?.max_tokens }}</el-descriptions-item>
          <el-descriptions-item label="Base URL">{{ currentConfig?.base_url || '使用默认' }}</el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer v-if="!isViewMode">
        <el-button @click="showDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">保存</el-button>
      </template>
      <template #footer v-else>
        <el-button @click="showDialog = false">关闭</el-button>
        <el-button type="primary" @click="switchToEdit">编辑</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useLLMStore } from '@/stores/llm'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import type { LLMConfig } from '@/api/types'

const llmStore = useLLMStore()
const configs = computed(() => llmStore.configs)

const showDialog = ref(false)
const isViewMode = ref(false)
const editingConfig = ref<LLMConfig | null>(null)
const viewingConfig = ref<LLMConfig | null>(null)
const currentConfig = computed(() => viewingConfig.value || editingConfig.value)

const formData = ref({
  name: '',
  provider: 'deepseek' as any,
  api_key: '',
  base_url: '',
  model: '',
  temperature: 0.7,
  max_tokens: 4096,
  is_default: false
})

const dialogTitle = computed(() => {
  if (isViewMode.value) return '查看配置'
  return editingConfig.value ? '编辑配置' : '新建配置'
})

const providerLabels: Record<string, string> = {
  deepseek: 'DeepSeek',
  openai: 'OpenAI',
  anthropic: 'Anthropic',
  ollama: 'Ollama',
  openai_compatible: 'OpenAI兼容'
}

const defaultUrls: Record<string, string> = {
  deepseek: 'https://api.deepseek.com',
  openai: 'https://api.openai.com/v1',
  anthropic: 'https://api.anthropic.com',
  ollama: 'http://localhost:11434',
  openai_compatible: ''
}

onMounted(async () => {
  await llmStore.fetchConfigs()
})

function providerLabel(provider: string) {
  return providerLabels[provider] || provider
}

function setDefaultUrl() {
  formData.value.base_url = defaultUrls[formData.value.provider] || ''
}

function openCreateDialog() {
  isViewMode.value = false
  editingConfig.value = null
  viewingConfig.value = null
  resetForm()
  showDialog.value = true
}

function handleView(config: LLMConfig) {
  viewingConfig.value = config
  editingConfig.value = null
  isViewMode.value = true
  showDialog.value = true
}

function handleEdit(config: LLMConfig) {
  editingConfig.value = config
  viewingConfig.value = null
  isViewMode.value = false
  formData.value = {
    name: config.name,
    provider: config.provider as any,
    api_key: config.api_key || '',
    base_url: config.base_url || '',
    model: config.model,
    temperature: config.temperature,
    max_tokens: config.max_tokens,
    is_default: config.is_default
  }
  showDialog.value = true
}

function switchToEdit() {
  if (viewingConfig.value) {
    handleEdit(viewingConfig.value)
  }
}

async function handleCreate() {
  try {
    if (editingConfig.value) {
      await llmStore.updateConfig(editingConfig.value.id, formData.value)
      ElMessage.success('配置更新成功')
    } else {
      await llmStore.createConfig(formData.value)
      ElMessage.success('配置创建成功')
    }
    showDialog.value = false
    resetForm()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function handleSetDefault(id: number) {
  await llmStore.setDefault(id)
  ElMessage.success('已设为默认配置')
}

async function handleTest(id: number) {
  const loadingMsg = ElMessage.info({ message: '正在测试连接...', duration: 0 })
  try {
    const result = await llmStore.testConfig(id)
    loadingMsg.close()
    const latency = result.latency_ms ? ` (耗时: ${result.latency_ms}ms)` : ''
    ElMessage.success(`连接测试成功！${latency}`)
  } catch (e: any) {
    loadingMsg.close()
    const errorMsg = e?.response?.data?.message || e?.message || '连接测试失败'
    ElMessage.error(errorMsg)
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定删除此配置？', '确认', { type: 'warning' })
  await llmStore.deleteConfig(id)
  ElMessage.success('配置已删除')
}

function resetForm() {
  editingConfig.value = null
  viewingConfig.value = null
  isViewMode.value = false
  formData.value = {
    name: '',
    provider: 'deepseek',
    api_key: '',
    base_url: '',
    model: '',
    temperature: 0.7,
    max_tokens: 4096,
    is_default: false
  }
}
</script>

<style scoped>
.llm-page {
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

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.config-card {
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

.config-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.config-card.default {
  border-color: var(--el-color-success);
  box-shadow: 0 0 8px rgba(103, 194, 58, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.config-name {
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

.config-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.info-item .label {
  color: var(--el-text-color-secondary);
}

.info-item .value {
  color: var(--el-text-color-primary);
  font-family: monospace;
  font-weight: 500;
}

.card-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.view-mode {
  padding: 20px 0;
}
</style>
