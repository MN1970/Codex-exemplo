import { beforeEach, describe, expect, it } from 'vitest'
import { useAuthStore } from '@/store/useAuthStore'
import type { UserPublic } from '@/types/auth'

const user: UserPublic = {
  id: 'user-1',
  email: 'ana@example.com',
  full_name: 'Ana',
  is_active: true,
  is_superuser: false,
}

function resetStore() {
  useAuthStore.setState({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
  })
  localStorage.clear()
}

describe('useAuthStore', () => {
  beforeEach(resetStore)

  it('starts unauthenticated with no user or tokens', () => {
    const state = useAuthStore.getState()
    expect(state.isAuthenticated).toBe(false)
    expect(state.user).toBeNull()
    expect(state.accessToken).toBeNull()
    expect(state.refreshToken).toBeNull()
  })

  it('setAuth stores tokens and flips isAuthenticated, optionally the user', () => {
    useAuthStore
      .getState()
      .setAuth({ accessToken: 'access-1', refreshToken: 'refresh-1' }, user)

    const state = useAuthStore.getState()
    expect(state.accessToken).toBe('access-1')
    expect(state.refreshToken).toBe('refresh-1')
    expect(state.isAuthenticated).toBe(true)
    expect(state.user).toEqual(user)
  })

  it('setAuth without a user leaves any existing user untouched', () => {
    useAuthStore
      .getState()
      .setAuth({ accessToken: 'access-1', refreshToken: 'refresh-1' }, user)
    useAuthStore
      .getState()
      .setAuth({ accessToken: 'access-2', refreshToken: 'refresh-2' })

    const state = useAuthStore.getState()
    expect(state.accessToken).toBe('access-2')
    expect(state.user).toEqual(user)
  })

  it('setTokens rotates tokens without touching the profile', () => {
    useAuthStore
      .getState()
      .setAuth({ accessToken: 'a1', refreshToken: 'r1' }, user)
    useAuthStore.getState().setTokens({ accessToken: 'a2', refreshToken: 'r2' })

    const state = useAuthStore.getState()
    expect(state.accessToken).toBe('a2')
    expect(state.refreshToken).toBe('r2')
    expect(state.user).toEqual(user)
    expect(state.isAuthenticated).toBe(true)
  })

  it('setUser updates only the profile', () => {
    useAuthStore.getState().setUser(user)
    expect(useAuthStore.getState().user).toEqual(user)
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
  })

  it('logout clears user, tokens and isAuthenticated', () => {
    useAuthStore
      .getState()
      .setAuth({ accessToken: 'a1', refreshToken: 'r1' }, user)
    useAuthStore.getState().logout()

    const state = useAuthStore.getState()
    expect(state.user).toBeNull()
    expect(state.accessToken).toBeNull()
    expect(state.refreshToken).toBeNull()
    expect(state.isAuthenticated).toBe(false)
  })

  it('persists auth state to localStorage under "manta-auth"', () => {
    useAuthStore
      .getState()
      .setAuth({ accessToken: 'a1', refreshToken: 'r1' }, user)

    const raw = localStorage.getItem('manta-auth')
    expect(raw).not.toBeNull()
    const parsed = JSON.parse(raw as string)
    expect(parsed.state.accessToken).toBe('a1')
    expect(parsed.state.user).toEqual(user)
  })
})
