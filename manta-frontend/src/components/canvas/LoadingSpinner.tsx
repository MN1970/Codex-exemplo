import { Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface LoadingSpinnerProps {
  className?: string
  size?: 'sm' | 'md' | 'lg'
  /** Optional text next to the spinner (e.g. "Carregando agentes…"). */
  label?: string
}

const SIZE_CLASSES: Record<NonNullable<LoadingSpinnerProps['size']>, string> = {
  sm: 'h-4 w-4',
  md: 'h-5 w-5',
  lg: 'h-8 w-8',
}

/** Small reusable spinner used across the Canvas while data streams in. */
export function LoadingSpinner({
  className,
  size = 'md',
  label,
}: LoadingSpinnerProps) {
  return (
    <div
      role="status"
      className={cn('flex items-center gap-2 text-muted-foreground', className)}
    >
      <Loader2 className={cn('animate-spin', SIZE_CLASSES[size])} aria-hidden="true" />
      {label ? <span className="text-sm">{label}</span> : null}
      <span className="sr-only">{label ?? 'Carregando…'}</span>
    </div>
  )
}
