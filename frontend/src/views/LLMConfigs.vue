<template>
  <div class="llm-page">
    <div class="page-header">
      <h2>LLM 配置</h2>
      <el-button type="primary" @click="showCreateDialog = true">新建配置</el-button>
    </div>

    <div class="config-list">
      <el-card v-if="defaultConfig" class="config-card default">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <span class="config-name">{{ defaultConfig.name }}</span>
              <el-tag type="success" size="small">默认</el-tag>
            </div>
            <div class="header-right">
              <el-tag size="small">{{ providerLabel(defaultConfig.provider) }}</el-tag>
            </div>
          </div>
        </template>
        <div class="config-info">
          <div class="info-row">
            <span class="label">模型:</span>
            <span class="value">{{ defaultConfig.model }}</span>
          </div>
          <div class="info-row">
            <span class="label">Base URL:</span>
            <span class="value">{{ defaultConfig.base_url || '使用默认' }}</span>
          </div>
          <div class="info-row">
            <span class="label">Temperature:</span>
            <span class="value">{{ defaultConfig.temperature }}</span>
          </div>
          <div class="info-row">
            <span class="label">Max Tokens:</span>
            <span class="value">{{ defaultConfig.max_tokens }}</span>
          </div>
        </div>
        <template #footer>
          <div class="card-footer">
            <el-button size="small" @click="handleEdit(defaultConfig)">编辑</el-button>
            <el-button size="small" @click="handleTest(defaultConfig.id)">测试连接</el-button>
          </div>
        </template>
      </el-card>

      <el-card v-for="config in nonDefaultConfigs" :key="config.id" class="config-card">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <span class="config-name">{{ config.name }}</span>
            </div>
            <div class="header-right">
              <el-tag size="small">{{ providerLabel(config.provider) }}</el-tag>
              <el-button size="small" link @click="handleSetDefault(config.id)">设为默认</el-button>
            </div>
          </div>
        </template>
        <div class="config-info">
          <div class="info-row">
            <span class="label">模型:</span>
            <span class="value">{{ config.model }}</span>
          </div>
          <div class="info-row">
            <span class="label">Base URL:</span>
            <span class="value">{{ config.base_url || '使用默认' }}</span>
          </div>
          <div class="info-row">
            <span class="label">Temperature:</span>
            <span class="value">{{ config.temperature }}</span>
          </div>
        </div>
        <template #footer>
          <div class="card-footer">
            <el-button size="small" @click="handleEdit(config)">编辑</el-button>
            <el-button size="small" @click="handleTest(config.id)">测试连接</el-button>
            <el-button size="small" type="danger" @click="handleDelete(config.id)">删除</el-button>
          </div>
        </template>
      </el-card>
    </div>

    <el-dialog v-model="showCreateDialog" :title="editingConfig ? '编辑配置' : '新建配置'" width="600px">
      <el-form :model="formData" label-width="120px">
        <el-form-item label="配置名称" required>
          <el-input v-model="formData.name" placeholder="例如: DeepSeek Chat" />
        </el-form-item>
        <el-form-item label="提供商" required>
          <el-select v-model="formData.provider" placeholder="选择提供商">
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
          <el-input-number v-model="formData.max_tokens" :min="1" :max="128000" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="formData.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useLLMStore } from '@/stores/llm'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { LLMConfig } from '@/api/types'

const llmStore = useLLMStore()
const configs = computed(() => llmStore.configs)
const defaultConfig = computed(() => llmStore.defaultConfig)
const nonDefaultConfigs = computed(() => llmStore.nonDefaultConfigs)
const loading = computed(() => llmStore.loading)

const showCreateDialog = ref(false)
const editingConfig = ref<LLMConfig | null>(null)

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

async function handleCreate() {
  try {
    if (editingConfig.value) {
      await llmStore.updateConfig(editingConfig.value.id, formData.value)
      ElMessage.success('配置更新成功')
    } else {
      await llmStore.createConfig(formData.value)
      ElMessage.success('配置创建成功')
    }
    showCreateDialog.value = false
    resetForm()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function handleEdit(config: LLMConfig) {
  editingConfig.value = config
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
  showCreateDialog.value = true
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
    if (result.status === 'success') {
      ElMessage.success('连接测试成功！')
    } else {
      ElMessage.error(result.message || '连接测试失败')
    }
  } catch (e) {
    loadingMsg.close()
    ElMessage.error('连接测试失败')
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定删除此配置？', '确认', { type: 'warning' })
  await llmStore.deleteConfig(id)
  ElMessage.success('配置已删除')
}

function resetForm() {
  editingConfig.value = null
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

.config-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.config-card {
  margin-bottom: 0;
}

.config-card.default {
  border-color: var(--color-success);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left,
.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.config-name {
  font-weight: 600;
  font-size: 16px;
}

.config-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-row {
  display: flex;
  gap: 8px;
}

.info-row .label {
  width: 100px;
  color: var(--text-color-secondary);
}

.info-row .value {
  color: var(--text-color-regular);
  font-family: monospace;
}

.card-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
