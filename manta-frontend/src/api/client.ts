import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { env } from '@/lib/env'

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
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`)
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
    }
    return Promise.reject(error)
  },
)

export default apiClient
