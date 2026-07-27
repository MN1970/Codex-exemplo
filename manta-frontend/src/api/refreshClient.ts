import axios from 'axios'
import { env } from '@/lib/env'
import type { TokenResponse } from '@/types/auth'

/**
 * Bare `axios.post`, deliberately not routed through `apiClient`.
 *
 * `apiClient`'s response interceptor (in `api/client.ts`) calls this to
 * rotate the refresh token whenever a request 401s. If it used `apiClient`
 * instead, a 401 on `/auth/refresh` itself would re-enter that same
 * interceptor and recurse. Keep this module free of any dependency on
 * `apiClient` or the auth store.
 */
export async function requestTokenRefresh(
  refreshToken: string,
): Promise<TokenResponse> {
  const { data } = await axios.post<TokenResponse>(
    `${env.apiBaseUrl}/auth/refresh`,
    { refresh_token: refreshToken },
  )
  return data
}
