import { api } from './index'
import type { Task } from './types'

export type { Task } from './types'

export interface TaskCreate {
  name: string
  description?: string
  target_url?: string
  prompt_id?: number
  llm_config_id?: number
  schedule: {
    type: string
    time?: string
    day_of_week?: number
    interval?: number
    cron?: string
  }
  max_items?: number
  requires_login?: boolean
  depends_on?: number
}

export const tasksApi = {
  list: (isEnabled?: boolean) =>
    api.get<Task[]>('/tasks', { params: { is_enabled: isEnabled } }),

  get: (id: number) =>
    api.get<Task>(`/tasks/${id}`),

  create: (data: TaskCreate) =>
    api.post<Task>('/tasks', data),

  update: (id: number, data: Partial<TaskCreate>) =>
    api.put<Task>(`/tasks/${id}`, data),

  delete: (id: number) =>
    api.delete<void>(`/tasks/${id}`),

  toggle: (id: number) =>
    api.post<Task>(`/tasks/${id}/toggle`),

  run: (id: number) =>
    api.post<{ message: string; execution_id: number | null }>(`/tasks/${id}/run`),

  stop: (id: number) =>
    api.post<{ message: string }>(`/tasks/${id}/stop`)
}
