import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import type { UserPublic } from '@/types/auth'

export interface AuthTokens {
  accessToken: string
  refreshToken: string
}

interface AuthState {
  user: UserPublic | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean

  /** Store tokens (post login/register/refresh), optionally the user too. */
  setAuth: (tokens: AuthTokens, user?: UserPublic | null) => void
  /** Update just the profile, e.g. after fetching `/auth/me`. */
  setUser: (user: UserPublic | null) => void
  /** Swap tokens without touching the profile — used by the refresh flow. */
  setTokens: (tokens: AuthTokens) => void
  /** Clear all auth state (manual logout, or a failed token refresh). */
  logout: () => void
}

/**
 * Global auth store (zustand). Persisted to `localStorage` under
 * `manta-auth` so the JWT survives page reloads; `api/client.ts` reads
 * `accessToken`/`refreshToken` from here (via `getState()`) rather than
 * touching `localStorage` directly, so this store is the single source
 * of truth for auth state.
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      setAuth: (tokens, user) =>
        set((state) => ({
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken,
          isAuthenticated: true,
          user: user === undefined ? state.user : user,
        })),

      setUser: (user) => set({ user }),

      setTokens: (tokens) =>
        set({
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken,
          isAuthenticated: true,
        }),

      logout: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: 'manta-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
)
