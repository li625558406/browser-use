<template>
  <div class="prompts-page">
    <div class="page-header">
      <h2>Prompt 管理</h2>
      <el-button type="primary" @click="showCreateDialog = true">新建 Prompt</el-button>
    </div>

    <el-tabs v-model="activeCategory">
      <el-tab-pane label="全部" name="all">
        <div class="prompt-list">
          <el-card v-for="prompt in prompts" :key="prompt.id" class="prompt-card">
            <template #header>
              <div class="card-header">
                <span class="prompt-name">{{ prompt.name }}</span>
                <div class="card-actions">
                  <el-tag size="small">{{ prompt.category || '未分类' }}</el-tag>
                  <el-tag size="small" type="info">v{{ prompt.version }}</el-tag>
                </div>
              </div>
            </template>
            <p v-if="prompt.description" class="prompt-description">{{ prompt.description }}</p>
            <div class="prompt-content">
              <pre>{{ prompt.content.slice(0, 200) }}{{ prompt.content.length > 200 ? '...' : '' }}</pre>
            </div>
            <div v-if="prompt.variables && prompt.variables.length > 0" class="prompt-variables">
              <span class="variables-label">变量:</span>
              <el-tag v-for="v in prompt.variables" :key="v" size="small" class="variable-tag">{{ v }}</el-tag>
            </div>
            <template #footer>
              <div class="card-footer">
                <el-button size="small" @click="handleEdit(prompt)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDelete(prompt.id)">删除</el-button>
              </div>
            </template>
          </el-card>
        </div>
      </el-tab-pane>
      <el-tab-pane v-for="category in categories" :key="category" :label="category" :name="category">
        <div class="prompt-list">
          <el-card v-for="prompt in getPromptsByCategory(category)" :key="prompt.id" class="prompt-card">
            <template #header>
              <div class="card-header">
                <span class="prompt-name">{{ prompt.name }}</span>
                <div class="card-actions">
                  <el-tag size="small" type="info">v{{ prompt.version }}</el-tag>
                </div>
              </div>
            </template>
            <p v-if="prompt.description" class="prompt-description">{{ prompt.description }}</p>
            <div class="prompt-content">
              <pre>{{ prompt.content.slice(0, 200) }}{{ prompt.content.length > 200 ? '...' : '' }}</pre>
            </div>
            <template #footer>
              <div class="card-footer">
                <el-button size="small" @click="handleEdit(prompt)">编辑</el-button>
                <el-button size="small" type="danger" @click="handleDelete(prompt.id)">删除</el-button>
              </div>
            </template>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showCreateDialog" :title="editingPrompt ? '编辑 Prompt' : '新建 Prompt'" width="700px">
      <el-form :model="formData" label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="formData.name" placeholder="输入 Prompt 名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="2" placeholder="简要描述此 Prompt 的用途" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="formData.category" placeholder="选择或输入分类">
            <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="formData.content" type="textarea" :rows="10" placeholder="输入 Prompt 内容，可以使用 {{variable}} 格式的变量" />
        </el-form-item>
        <el-form-item label="变量">
          <el-input v-model="variablesInput" placeholder="用逗号分隔，如: url, target_data" />
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
import { usePromptsStore } from '@/stores/prompts'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { Prompt } from '@/api/types'

const promptsStore = usePromptsStore()
const prompts = computed(() => promptsStore.prompts)
const promptsByCategory = computed(() => promptsStore.promptsByCategory)

const activeCategory = ref('all')
const showCreateDialog = ref(false)
const editingPrompt = ref<Prompt | null>(null)
const variablesInput = ref('')

const formData = ref({
  name: '',
  description: '',
  content: '',
  category: '',
  variables: [] as string[]
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

function handleEdit(prompt: Prompt) {
  editingPrompt.value = prompt
  formData.value = {
    name: prompt.name,
    description: prompt.description || '',
    content: prompt.content,
    category: prompt.category || '',
    variables: prompt.variables || []
  }
  variablesInput.value = (prompt.variables || []).join(', ')
  showCreateDialog.value = true
}

async function handleDelete(id: number) {
  await ElMessageBox.confirm('确定删除此 Prompt？', '确认', { type: 'warning' })
  await promptsStore.deletePrompt(id)
  ElMessage.success('Prompt 已删除')
}

function resetForm() {
  editingPrompt.value = null
  formData.value = {
    name: '',
    description: '',
    content: '',
    category: '',
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

.prompt-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.prompt-card {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.prompt-name {
  font-weight: 600;
  font-size: 16px;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.prompt-description {
  color: var(--text-color-secondary);
  margin: 0 0 12px 0;
}

.prompt-content {
  background: var(--bg-color);
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 12px;
}

.prompt-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  color: var(--text-color-regular);
}

.prompt-variables {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.variables-label {
  font-size: 14px;
  color: var(--text-color-secondary);
}

.variable-tag {
  font-family: monospace;
}

.card-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
</style>
