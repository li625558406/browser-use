import { api } from './index'
import type { Prompt } from './types'

export interface PromptCreate {
  name: string
  description?: string
  content: string
  category?: string
  variables?: string[]
}

export const promptsApi = {
  list: (category?: string) =>
    api.get<Prompt[]>('/prompts', { params: { category } }),

  get: (id: number) =>
    api.get<Prompt>(`/prompts/${id}`),

  create: (data: PromptCreate) =>
    api.post<Prompt>('/prompts', data),

  update: (id: number, data: Partial<PromptCreate>) =>
    api.put<Prompt>(`/prompts/${id}`, data),

  delete: (id: number) =>
    api.delete<void>(`/prompts/${id}`)
}
