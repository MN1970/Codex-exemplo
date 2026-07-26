import { Link } from 'react-router-dom'
import { ThemeToggle } from '@/components/ThemeToggle'
import { env } from '@/lib/env'

export function Header() {
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
        </nav>
      </div>
    </header>
  )
}
