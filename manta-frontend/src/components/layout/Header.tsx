import { Link, useNavigate } from 'react-router-dom'
import { ThemeToggle } from '@/components/ThemeToggle'
import { Button } from '@/components/ui/button'
import { env } from '@/lib/env'
import { useAuthStore } from '@/store/useAuthStore'

export function Header() {
  const navigate = useNavigate()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="sticky top-0 z-10 border-b border-border bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link to="/" className="text-sm font-semibold tracking-tight">
          {env.appName}
        </Link>
        <nav className="flex items-center gap-4 text-sm text-muted-foreground">
          <Link to="/" className="hover:text-foreground">
            Home
          </Link>
          <ThemeToggle />
          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              {user?.email && (
                <span className="hidden text-xs sm:inline">{user.email}</span>
              )}
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Sair
              </Button>
            </div>
          ) : (
            <Link to="/login" className="hover:text-foreground">
              Entrar
            </Link>
          )}
        </nav>
      </div>
    </header>
  )
}
