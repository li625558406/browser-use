export interface Task {
  id: number
  name: string
  description: string | null
  target_url: string | null
  prompt_id: number | null
  llm_config_id: number | null
  schedule_type: string
  schedule_config: any
  browser_mode: string
  profile_name: string | null
  is_enabled: boolean
  max_items: number | null
  requires_login: boolean
  depends_on: number | null
  created_at: string
  updated_at: string
}

export interface Prompt {
  id: number
  name: string
  description: string | null
  content: string
  category: string | null
  variables: string[] | null
  version: number
  created_at: string
  updated_at: string
}

export interface LLMConfig {
  id: number
  name: string
  provider: string
  api_key: string | null
  base_url: string | null
  model: string
  temperature: number
  max_tokens: number
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface TaskExecution {
  id: number
  task_id: number
  task_name: string
  status: string
  started_at: string | null
  completed_at: string | null
  error_message: string | null
  log_content: string | null
  screenshot_path: string | null
}

export interface ChromeProfile {
  name: string
  path: string
}

export interface BrowserStatus {
  is_connected: boolean
  cdp_url: string | null
  profiles: ChromeProfile[]
}
