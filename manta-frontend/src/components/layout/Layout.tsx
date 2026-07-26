import { Outlet } from 'react-router-dom'
import { Header } from '@/components/layout/Header'

/**
 * Root layout rendered around every route via <Outlet />.
 * Add a <Sidebar /> or <Footer /> here as the app grows.
 */
export function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <Header />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
