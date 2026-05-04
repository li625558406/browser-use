import { api } from './index'
import type { TaskExecution } from './types'

export const executionsApi = {
  list: (taskId?: number) =>
    api.get<TaskExecution[]>('/executions', { params: { task_id: taskId } }),

  get: (id: number) =>
    api.get<TaskExecution>(`/executions/${id}`)
}
