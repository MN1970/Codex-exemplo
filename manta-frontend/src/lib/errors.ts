import { isAxiosError } from 'axios'
import { isMultiOrgErrorDetail, type MultiOrgErrorDetail } from '@/types/auth'

/**
 * Turn any thrown value — ideally an `AxiosError` from a FastAPI backend
 * whose error body is `{ detail: string | object }` — into a message safe
 * to show a user. Falls back to a generic message rather than leaking
 * raw error internals.
 */
export function getErrorMessage(
  error: unknown,
  fallback = 'Algo deu errado. Tente novamente.',
): string {
  if (isAxiosError(error)) {
    const detail = (error.response?.data as { detail?: unknown } | undefined)
      ?.detail
    if (typeof detail === 'string') return detail
    if (isMultiOrgErrorDetail(detail)) return detail.message
    if (error.message) return error.message
  }
  if (error instanceof Error) return error.message
  return fallback
}

/**
 * If the error is the backend's "user belongs to multiple orgs, pick one"
 * 400 response, return its structured detail so the UI can render an org
 * picker; otherwise `null`.
 */
export function getMultiOrgErrorDetail(
  error: unknown,
): MultiOrgErrorDetail | null {
  if (!isAxiosError(error) || error.response?.status !== 400) return null
  const detail = (error.response?.data as { detail?: unknown } | undefined)
    ?.detail
  return isMultiOrgErrorDetail(detail) ? detail : null
}
