import { api } from './index'
import type { BrowserStatus, ChromeProfile } from './types'

export const browserApi = {
  listProfiles: () =>
    api.get<ChromeProfile[]>('/browser/profiles'),

  getStatus: () =>
    api.get<BrowserStatus>('/browser/status'),

  testConnection: (cdpPort: number = 9242) =>
    api.post<{ success: boolean; message: string }>('/browser/test-connection', null, { params: { cdp_port: cdpPort } })
}
