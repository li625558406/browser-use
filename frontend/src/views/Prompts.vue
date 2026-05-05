<template>
  <div class="prompts-page">
    <div class="page-header">
      <h2>Prompt 管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">新建 Prompt</el-button>
    </div>

    <el-tabs v-model="activeCategory">
      <el-tab-pane label="全部" name="all">
        <div class="prompt-grid">
          <div v-for="prompt in prompts" :key="prompt.id" class="prompt-card" @click="handleView(prompt)">
            <div class="card-header">
              <span class="prompt-name">{{ prompt.name }}</span>
              <div class="card-meta">
                <el-tag size="small" v-if="prompt.category">{{ prompt.category }}</el-tag>
                <el-tag size="small" type="info" v-if="prompt.version">v{{ prompt.version }}</el-tag>
              </div>
            </div>
            <p v-if="prompt.description" class="prompt-description">{{ prompt.description }}</p>
            <div class="card-footer">
              <el-button size="small" @click.stop="handleEdit(prompt)">编辑</el-button>
              <el-button size="small" type="danger" @click.stop="handleDelete(prompt.id)">删除</el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane v-for="category in categories" :key="category" :label="category" :name="category">
        <div class="prompt-grid">
          <div v-for="prompt in getPromptsByCategory(category)" :key="prompt.id" class="prompt-card" @click="handleView(prompt)">
            <div class="card-header">
              <span class="prompt-name">{{ prompt.name }}</span>
              <div class="card-meta">
                <el-tag size="small" type="info" v-if="prompt.version">v{{ prompt.version }}</el-tag>
              </div>
            </div>
            <p v-if="prompt.description" class="prompt-description">{{ prompt.description }}</p>
            <div class="card-footer">
              <el-button size="small" @click.stop="handleEdit(prompt)">编辑</el-button>
              <el-button size="small" type="danger" @click.stop="handleDelete(prompt.id)">删除</el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 查看/编辑对话框 -->
    <el-dialog v-model="showCreateDialog" :title="dialogTitle" width="800px" @closed="resetForm">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="formData.name" placeholder="输入 Prompt 名称" :disabled="isViewMode" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="简要描述此 Prompt 的用途" :disabled="isViewMode" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="formData.category" placeholder="选择或输入分类" :disabled="isViewMode" style="width: 100%">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本">
          <el-input v-model="formData.version" placeholder="如: 1.0" :disabled="isViewMode" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="formData.content" type="textarea" :rows="12" placeholder="输入 Prompt 内容，可以使用 {{variable}} 格式的变量" :disabled="isViewMode" />
        </el-form-item>
        <el-form-item label="变量">
          <el-input v-model="variablesInput" placeholder="用逗号分隔，如: url, target_data" :disabled="isViewMode" />
        </el-form-item>
      </el-form>
      <template #footer v-if="!isViewMode">
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">保存</el-button>
      </template>
      <template #footer v-else>
        <el-button @click="showCreateDialog = false">关闭</el-button>
        <el-button type="primary" @click="switchToEdit">编辑</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePromptsStore } from '@/stores/prompts'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Prompt } from '@/api/types'

const promptsStore = usePromptsStore()
const prompts = computed(() => promptsStore.prompts)
const promptsByCategory = computed(() => promptsStore.promptsByCategory)

const activeCategory = ref('all')
const showCreateDialog = ref(false)
const isViewMode = ref(false)
const editingPrompt = ref<Prompt | null>(null)
const viewingPrompt = ref<Prompt | null>(null)
const variablesInput = ref('')

const formData = ref({
  name: '',
  description: '',
  content: '',
  category: '',
  version: 1,
  variables: [] as string[]
})

const dialogTitle = computed(() => {
  if (isViewMode.value) return '查看 Prompt'
  return editingPrompt.value ? '编辑 Prompt' : '新建 Prompt'
})

const categories = computed(() => {
  const cats = new Set(prompts.value.map(p => p.category).filter(Boolean))
  return Array.from(cats)
})

onMounted(async () => {
  await promptsStore.fetchPrompts()
})

function getPromptsByCategory(category: string | null) {
  if (!category) return []
  return promptsByCategory.value[category] || []
}

function handleView(prompt: Prompt) {
  viewingPrompt.value = prompt
  editingPrompt.value = null
  isViewMode.value = true
  formData.value = {
    name: prompt.name,
    description: prompt.description || '',
    content: prompt.content,
    category: prompt.category || '',
    version: prompt.version,
    variables: prompt.variables || []
  }
  variablesInput.value = (prompt.variables || []).join(', ')
  showCreateDialog.value = true
}

function handleEdit(prompt: Prompt) {
  editingPrompt.value = prompt
  viewingPrompt.value = null
  isViewMode.value = false
  formData.value = {
    name: prompt.name,
    description: prompt.description || '',
    content: prompt.content,
    category: prompt.category || '',
    version: prompt.version,
    variables: prompt.variables || []
  }
  variablesInput.value = (prompt.variables || []).join(', ')
  showCreateDialog.value = true
}

function switchToEdit() {
  if (viewingPrompt.value) {
    handleEdit(viewingPrompt.value)
  }
}

async function handleCreate() {
  try {
    formData.value.variables = variablesInput.value.split(',').map(v => v.trim()).filter(Boolean)
    if (editingPrompt.value) {
      await promptsStore.updatePrompt(editingPrompt.value.id, formData.value)
      ElMessage.success('Prompt 更新成功')
    } else {
      await promptsStore.createPrompt(formData.value)
      ElMessage.success('Prompt 创建成功')
    }
    showCreateDialog.value = false
    resetForm()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定删除此 Prompt？', '确认', { type: 'warning' })
  await promptsStore.deletePrompt(id)
  ElMessage.success('Prompt 已删除')
}

function resetForm() {
  editingPrompt.value = null
  viewingPrompt.value = null
  isViewMode.value = false
  formData.value = {
    name: '',
    description: '',
    content: '',
    category: '',
    version: 1,
    variables: []
  }
  variablesInput.value = ''
}
</script>

<style scoped>
.prompts-page {
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

.prompt-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.prompt-card {
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

.prompt-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.prompt-name {
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

.prompt-description {
  color: var(--el-text-color-secondary);
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
}
</style>
