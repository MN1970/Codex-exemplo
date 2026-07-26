import { apiClient } from '@/api/client'
import type {
  LoginPayload,
  MeResponse,
  RegisterPayload,
  RegisterResponse,
  TokenResponse,
} from '@/types/auth'

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', payload)
  return data
}

export async function register(
  payload: RegisterPayload,
): Promise<RegisterResponse> {
  const { data } = await apiClient.post<RegisterResponse>(
    '/auth/register',
    payload,
  )
  return data
}

export async function fetchMe(): Promise<MeResponse> {
  const { data } = await apiClient.get<MeResponse>('/auth/me')
  return data
}
