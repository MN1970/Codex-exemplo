import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { env } from '@/lib/env'
import { requestTokenRefresh } from '@/api/refreshClient'
import { useAuthStore } from '@/store/useAuthStore'

/**
 * Shared axios instance for all API calls. Import this rather than
 * calling `axios` directly so auth headers, base URL and error handling
 * stay consistent across the app.
 */
export const apiClient = axios.create({
  baseURL: env.apiBaseUrl,
  timeout: 15_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }
  return config
})

type RetriableConfig = InternalAxiosRequestConfig & { _retry?: boolean }

// Auth endpoints never trigger the refresh flow themselves — a 401 from
// /login or /register is just "bad credentials", and a 401 from /refresh
// means the refresh token itself is dead (handled by clearing auth below).
const AUTH_ENDPOINTS = ['/auth/login', '/auth/register', '/auth/refresh']

function isAuthEndpoint(url: string | undefined): boolean {
  return !!url && AUTH_ENDPOINTS.some((path) => url.includes(path))
}

// De-dupe concurrent refreshes: if five requests 401 at once, they should
// share a single POST /auth/refresh instead of racing five rotations
// against a refresh token that's only valid for one use.
let refreshPromise: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const { refreshToken, setTokens, logout } = useAuthStore.getState()
  if (!refreshToken) return null

  try {
    const tokens = await requestTokenRefresh(refreshToken)
    setTokens({
      accessToken: tokens.access_token,
      refreshToken: tokens.refresh_token,
    })
    return tokens.access_token
  } catch {
    logout()
    return null
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined

    const shouldAttemptRefresh =
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      !isAuthEndpoint(original.url)

    if (shouldAttemptRefresh) {
      original._retry = true
      refreshPromise ??= refreshAccessToken().finally(() => {
        refreshPromise = null
      })
      const newAccessToken = await refreshPromise

      if (newAccessToken) {
        original.headers.set('Authorization', `Bearer ${newAccessToken}`)
        return apiClient(original)
      }
    }

    if (error.response?.status === 401 && !isAuthEndpoint(original?.url)) {
      useAuthStore.getState().logout()
    }

    return Promise.reject(error)
  },
)

export default apiClient
