import { api } from './index'
import type { TaskExecution } from './types'

export const executionsApi = {
  list: (taskId?: number, status?: string) =>
    api.get<TaskExecution[]>('/executions', { params: { task_id: taskId, status } }),

  get: (id: number) =>
    api.get<TaskExecution>(`/executions/${id}`),

  delete: (id: number) =>
    api.delete<void>(`/executions/${id}`)
}
