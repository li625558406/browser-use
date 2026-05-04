import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { tasksApi, type TaskCreate } from '@/api/tasks'
import type { Task } from '@/api/types'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const enabledTasks = computed(() => tasks.value.filter(t => t.is_enabled))
  const disabledTasks = computed(() => tasks.value.filter(t => !t.is_enabled))

  async function fetchTasks() {
    loading.value = true
    error.value = null
    try {
      tasks.value = await tasksApi.list()
    } catch (e: any) {
      error.value = e.message || 'Failed to fetch tasks'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function createTask(data: TaskCreate) {
    loading.value = true
    error.value = null
    try {
      const newTask = await tasksApi.create(data)
      tasks.value.push(newTask)
      return newTask
    } catch (e: any) {
      error.value = e.message || 'Failed to create task'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function updateTask(id: number, data: Partial<TaskCreate>) {
    loading.value = true
    error.value = null
    try {
      const updated = await tasksApi.update(id, data)
      const index = tasks.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tasks.value[index] = updated
      }
      return updated
    } catch (e: any) {
      error.value = e.message || 'Failed to update task'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function deleteTask(id: number) {
    loading.value = true
    error.value = null
    try {
      await tasksApi.delete(id)
      tasks.value = tasks.value.filter(t => t.id !== id)
    } catch (e: any) {
      error.value = e.message || 'Failed to delete task'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function toggleTask(id: number) {
    loading.value = true
    error.value = null
    try {
      const updated = await tasksApi.toggle(id)
      const index = tasks.value.findIndex(t => t.id === id)
      if (index !== -1) {
        tasks.value[index] = updated
      }
      return updated
    } catch (e: any) {
      error.value = e.message || 'Failed to toggle task'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function runTask(id: number) {
    loading.value = true
    error.value = null
    try {
      const result = await tasksApi.run(id)
      return result
    } catch (e: any) {
      error.value = e.message || 'Failed to run task'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    tasks,
    loading,
    error,
    enabledTasks,
    disabledTasks,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTask,
    runTask
  }
})
