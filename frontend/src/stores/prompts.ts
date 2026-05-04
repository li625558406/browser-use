import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { promptsApi, type PromptCreate } from '@/api/prompts'
import type { Prompt } from '@/api/types'

export const usePromptsStore = defineStore('prompts', () => {
  const prompts = ref<Prompt[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const promptsByCategory = computed(() => {
    const grouped: Record<string, Prompt[]> = {}
    prompts.value.forEach(p => {
      const cat = p.category || 'uncategorized'
      if (!grouped[cat]) grouped[cat] = []
      grouped[cat].push(p)
    })
    return grouped
  })

  async function fetchPrompts() {
    loading.value = true
    error.value = null
    try {
      prompts.value = await promptsApi.list()
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch prompts'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createPrompt(data: PromptCreate) {
    loading.value = true
    error.value = null
    try {
      const newPrompt = await promptsApi.create(data)
      prompts.value.push(newPrompt)
      return newPrompt
    } catch (e: any) {
      error.value = e.message || 'Failed to create prompt'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updatePrompt(id: number, data: Partial<PromptCreate>) {
    loading.value = true
    error.value = null
    try {
      const updated = await promptsApi.update(id, data)
      const index = prompts.value.findIndex(p => p.id === id)
      if (index !== -1) {
        prompts.value[index] = updated
      }
      return updated
    } catch (e: any) {
      error.value = e.message || 'Failed to update prompt'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deletePrompt(id: number) {
    loading.value = true
    error.value = null
    try {
      await promptsApi.delete(id)
      prompts.value = prompts.value.filter(p => p.id !== id)
    } catch (e: any) {
      error.value = e.message || 'Failed to delete prompt'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    prompts,
    loading,
    error,
    promptsByCategory,
    fetchPrompts,
    createPrompt,
    updatePrompt,
    deletePrompt
  }
})
