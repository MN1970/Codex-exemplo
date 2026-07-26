import { useEffect, useState } from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/store/useAppStore'

export function Home() {
  const [count, setCount] = useState(0)
  const sidebarOpen = useAppStore((s) => s.sidebarOpen)
  const toggleSidebar = useAppStore((s) => s.toggleSidebar)

  useEffect(() => {
    document.title = 'Manta Frontend — Home'
  }, [])

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Manta Frontend</h1>
        <p className="mt-1 text-muted-foreground">
          Skeleton React + Vite + TypeScript. Edite{' '}
          <code className="rounded bg-muted px-1 py-0.5 font-mono text-sm">
            src/pages/Home.tsx
          </code>{' '}
          para começar.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Zustand</CardTitle>
            <CardDescription>Estado global de exemplo</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center gap-3">
            <Button onClick={() => setCount((c) => c + 1)}>
              Contador: {count}
            </Button>
            <Button variant="outline" onClick={toggleSidebar}>
              sidebarOpen: {String(sidebarOpen)}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Estrutura</CardTitle>
            <CardDescription>Pastas principais do projeto</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="list-inside list-disc text-sm text-muted-foreground">
              <li>api/ — cliente axios e endpoints</li>
              <li>store/ — zustand stores</li>
              <li>components/ — UI e layout</li>
              <li>pages/ — rotas</li>
              <li>lib/ — utilitários</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
