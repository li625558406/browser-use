import { api } from './index'
import type { LLMConfig } from './types'

export interface LLMConfigCreate {
  name: string
  provider: 'deepseek' | 'openai' | 'anthropic' | 'ollama' | 'openai_compatible'
  api_key?: string
  base_url?: string
  model: string
  temperature?: number
  max_tokens?: number
  is_default?: boolean
}

export const llmApi = {
  list: () =>
    api.get<LLMConfig[]>('/llm-configs'),

  get: (id: number) =>
    api.get<LLMConfig>(`/llm-configs/${id}`),

  create: (data: LLMConfigCreate) =>
    api.post<LLMConfig>('/llm-configs', data),

  update: (id: number, data: Partial<LLMConfigCreate>) =>
    api.put<LLMConfig>(`/llm-configs/${id}`, data),

  delete: (id: number) =>
    api.delete<void>(`/llm-configs/${id}`),

  setDefault: (id: number) =>
    api.post<LLMConfig>(`/llm-configs/${id}/set-default`),

  test: (id: number) =>
    api.post<{ status: string; message: string }>(`/llm-configs/${id}/test`)
}
