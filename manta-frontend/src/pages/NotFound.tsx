import { Link } from 'react-router-dom'
import { buttonVariants } from '@/components/ui/button'

export function NotFound() {
  return (
    <div className="flex flex-col items-center gap-4 py-24 text-center">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="text-muted-foreground">Página não encontrada.</p>
      <Link to="/" className={buttonVariants({ variant: 'default' })}>
        Voltar para o início
      </Link>
    </div>
  )
}
