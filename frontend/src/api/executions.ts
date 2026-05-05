import { api } from './index'
import type { TaskExecution } from './types'

export interface ExportFile {
  name: string
  size: string
  date: number
  path: string
}

export const executionsApi = {
  list: (taskId?: number, status?: string) =>
    api.get<TaskExecution[]>('/executions', { params: { task_id: taskId, status } }),

  get: (id: number) =>
    api.get<TaskExecution>(`/executions/${id}`),

  delete: (id: number) =>
    api.delete<void>(`/executions/${id}`),

  resume: (taskId: number) =>
    api.post<{ message: string }>(`/tasks/${taskId}/resume`),

  stop: (taskId: number) =>
    api.post<{ message: string }>(`/tasks/${taskId}/stop`),

  // 导出执行记录
  export: (id: number) => {
    // 直接打开下载链接
    window.open(`/api/executions/${id}/export`, '_blank')
  },

  // 获取导出文件列表
  listExports: () =>
    api.get<ExportFile[]>('/executions/exports/list'),

  // 下载导出文件
  downloadExport: (filename: string) => {
    window.open(`/api/executions/exports/${filename}`, '_blank')
  }
}
