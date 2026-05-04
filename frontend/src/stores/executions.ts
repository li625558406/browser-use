import { defineStore } from 'pinia'
import { ref } from 'vue'
import { executionsApi } from '@/api/executions'
import type { TaskExecution } from '@/api/types'

export const useExecutionsStore = defineStore('executions', () => {
  const executions = ref<TaskExecution[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchExecutions(taskId?: number, status?: string) {
    loading.value = true
    error.value = null
    try {
      executions.value = await executionsApi.list(taskId, status)
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch executions'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteExecution(id: number) {
    loading.value = true
    error.value = null
    try {
      await executionsApi.delete(id)
      executions.value = executions.value.filter(e => e.id !== id)
    } catch (e: any) {
      error.value = e.message || 'Failed to delete execution'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    executions,
    loading,
    error,
    fetchExecutions,
    deleteExecution
  }
})
