import { apiClient } from '@/api/client'

export interface HealthStatus {
  status: 'ok' | 'error'
  version?: string
}

/**
 * Example endpoint module. Add one file per resource/domain
 * (e.g. `users.ts`, `projects.ts`) following this pattern.
 */
export async function getHealth(): Promise<HealthStatus> {
  const { data } = await apiClient.get<HealthStatus>('/health')
  return data
}
