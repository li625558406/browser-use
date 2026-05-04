import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { llmApi, type LLMConfigCreate } from '@/api/llm'
import type { LLMConfig } from '@/api/types'

export const useLLMStore = defineStore('llm', () => {
  const configs = ref<LLMConfig[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const defaultConfig = computed(() => configs.value.find(c => c.is_default))
  const nonDefaultConfigs = computed(() => configs.value.filter(c => !c.is_default))

  async function fetchConfigs() {
    loading.value = true
    error.value = null
    try {
      configs.value = await llmApi.list()
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch LLM configs'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createConfig(data: LLMConfigCreate) {
    loading.value = true
    error.value = null
    try {
      const newConfig = await llmApi.create(data)
      configs.value.push(newConfig)
      return newConfig
    } catch (e: any) {
      error.value = e.message || 'Failed to create LLM config'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateConfig(id: number, data: Partial<LLMConfigCreate>) {
    loading.value = true
    error.value = null
    try {
      const updated = await llmApi.update(id, data)
      const index = configs.value.findIndex(c => c.id === id)
      if (index !== -1) {
        configs.value[index] = updated
      }
      return updated
    } catch (e: any) {
      error.value = e.message || 'Failed to update LLM config'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteConfig(id: number) {
    loading.value = true
    error.value = null
    try {
      await llmApi.delete(id)
      configs.value = configs.value.filter(c => c.id !== id)
    } catch (e: any) {
      error.value = e.message || 'Failed to delete LLM config'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function setDefault(id: number) {
    loading.value = true
    error.value = null
    try {
      const updated = await llmApi.setDefault(id)
      configs.value.forEach(c => c.is_default = c.id === id)
      return updated
    } catch (e: any) {
      error.value = e.message || 'Failed to set default config'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function testConfig(id: number) {
    loading.value = true
    error.value = null
    try {
      const result = await llmApi.test(id)
      return result
    } catch (e: any) {
      error.value = e.message || 'Failed to test LLM config'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    configs,
    loading,
    error,
    defaultConfig,
    nonDefaultConfigs,
    fetchConfigs,
    createConfig,
    updateConfig,
    deleteConfig,
    setDefault,
    testConfig
  }
})
