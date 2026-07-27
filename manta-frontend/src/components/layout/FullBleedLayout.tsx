import { Outlet } from 'react-router-dom'
import { Header } from '@/components/layout/Header'

/**
 * Alternate root layout for app-like pages (e.g. `/canvas`) that need
 * the full viewport height/width — unlike `<Layout />`, it doesn't
 * constrain `<Outlet />` to `max-w-6xl` with vertical padding. Keeps
 * the same global `<Header />` so nav/theme/logout stay consistent.
 */
export function FullBleedLayout() {
  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background text-foreground">
      <Header />
      <div className="min-h-0 flex-1">
        <Outlet />
      </div>
    </div>
  )
}
