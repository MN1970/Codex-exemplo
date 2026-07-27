import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/useAuthStore'

/**
 * Route guard: renders the matched child route (`<Outlet />`) only when
 * the auth store has a JWT; otherwise redirects to `/login`, remembering
 * the page the user was trying to reach in `location.state.from` so
 * `Login` can send them back after a successful sign-in.
 *
 * Usage (see `App.tsx`):
 *
 *   <Route element={<ProtectedRoute />}>
 *     <Route path="dashboard" element={<Dashboard />} />
 *   </Route>
 */
export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}
