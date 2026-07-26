import MockAdapter from 'axios-mock-adapter'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { apiClient } from '@/api/client'
import { requestTokenRefresh } from '@/api/refreshClient'
import { useAuthStore } from '@/store/useAuthStore'
import type { TokenResponse } from '@/types/auth'

vi.mock('@/api/refreshClient', () => ({
  requestTokenRefresh: vi.fn(),
}))

const mockedRefresh = vi.mocked(requestTokenRefresh)

const newTokens: TokenResponse = {
  access_token: 'new-access',
  refresh_token: 'new-refresh',
  token_type: 'bearer',
  expires_in: 900,
  org_id: null,
  roles: [],
}

let mock: MockAdapter

beforeEach(() => {
  mock = new MockAdapter(apiClient)
  useAuthStore.setState({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
  })
  localStorage.clear()
  mockedRefresh.mockReset()
})

afterEach(() => {
  mock.restore()
})

describe('apiClient request interceptor', () => {
  it('attaches the Authorization header from the auth store', async () => {
    useAuthStore
      .getState()
      .setAuth({ accessToken: 'tok-1', refreshToken: 'ref-1' })

    mock.onGet('/ping').reply((config) => {
      expect(config.headers?.Authorization).toBe('Bearer tok-1')
      return [200, { ok: true }]
    })

    const res = await apiClient.get('/ping')
    expect(res.status).toBe(200)
  })

  it('sends no Authorization header when logged out', async () => {
    mock.onGet('/ping').reply((config) => {
      expect(config.headers?.Authorization).toBeUndefined()
      return [200, { ok: true }]
    })

    await apiClient.get('/ping')
  })
})

describe('apiClient response interceptor — automatic refresh', () => {
  it('refreshes the access token on a 401 and retries the original request', async () => {
    useAuthStore
      .getState()
      .setAuth({ accessToken: 'expired-access', refreshToken: 'ref-1' })
    mockedRefresh.mockResolvedValue(newTokens)

    mock
      .onGet('/secret')
      .replyOnce(401)
      .onGet('/secret')
      .reply((config) => {
        expect(config.headers?.Authorization).toBe('Bearer new-access')
        return [200, { secret: 42 }]
      })

    const res = await apiClient.get('/secret')

    expect(res.status).toBe(200)
    expect(res.data).toEqual({ secret: 42 })
    expect(mockedRefresh).toHaveBeenCalledWith('ref-1')
    expect(useAuthStore.getState().accessToken).toBe('new-access')
    expect(useAuthStore.getState().refreshToken).toBe('new-refresh')
  })

  it('logs the user out when the refresh token itself is rejected', async () => {
    useAuthStore
      .getState()
      .setAuth({ accessToken: 'expired-access', refreshToken: 'dead-ref' })
    mockedRefresh.mockRejectedValue(new Error('refresh token expired'))

    mock.onGet('/secret').reply(401)

    await expect(apiClient.get('/secret')).rejects.toBeTruthy()

    expect(useAuthStore.getState().isAuthenticated).toBe(false)
    expect(useAuthStore.getState().accessToken).toBeNull()
  })

  it('never attempts a refresh for the auth endpoints themselves', async () => {
    useAuthStore
      .getState()
      .setAuth({ accessToken: 'expired-access', refreshToken: 'ref-1' })

    mock.onPost('/auth/login').reply(401, { detail: 'Credenciais inválidas.' })

    await expect(
      apiClient.post('/auth/login', { email: 'a@a.com', password: 'x' }),
    ).rejects.toBeTruthy()

    expect(mockedRefresh).not.toHaveBeenCalled()
  })

  it('de-dupes concurrent 401s into a single refresh call', async () => {
    useAuthStore
      .getState()
      .setAuth({ accessToken: 'expired-access', refreshToken: 'ref-1' })
    mockedRefresh.mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve(newTokens), 10)),
    )

    mock.onGet('/a').replyOnce(401).onGet('/a').reply(200, { ok: 'a' })
    mock.onGet('/b').replyOnce(401).onGet('/b').reply(200, { ok: 'b' })

    const [resA, resB] = await Promise.all([
      apiClient.get('/a'),
      apiClient.get('/b'),
    ])

    expect(resA.data).toEqual({ ok: 'a' })
    expect(resB.data).toEqual({ ok: 'b' })
    expect(mockedRefresh).toHaveBeenCalledTimes(1)
  })
})
