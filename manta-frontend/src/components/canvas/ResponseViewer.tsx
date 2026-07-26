import { AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { LoadingSpinner } from '@/components/canvas/LoadingSpinner'
import type { InvokeStatus } from '@/hooks/useAgentInvoke'

export interface ResponseViewerProps {
  status: InvokeStatus
  content: string
  error: string | null
  agentName?: string
  className?: string
}

/**
 * Renders the streamed reply from `useAgentInvoke`: empty state before
 * the first prompt, a spinner while waiting for the first token, the
 * growing text (with a blinking caret while still streaming), and the
 * error state if the SSE call failed.
 */
export function ResponseViewer({
  status,
  content,
  error,
  agentName,
  className,
}: ResponseViewerProps) {
  const showEmptyState = status === 'idle' && !content
  const showWaitingSpinner = status === 'streaming' && !content

  return (
    <div
      className={cn(
        'flex min-h-64 flex-1 flex-col overflow-y-auto rounded-lg border border-border bg-card p-4',
        className,
      )}
    >
      {showEmptyState && (
        <p className="m-auto max-w-sm text-center text-sm text-muted-foreground">
          {agentName
            ? `Envie um prompt para ${agentName} para ver a resposta aqui.`
            : 'Selecione um agente e envie um prompt para começar.'}
        </p>
      )}

      {showWaitingSpinner && (
        <div className="m-auto">
          <LoadingSpinner label="Aguardando resposta…" />
        </div>
      )}

      {content && (
        <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">
          {content}
          {status === 'streaming' && (
            <span
              aria-hidden="true"
              className="ml-0.5 inline-block h-4 w-1.5 translate-y-0.5 animate-pulse bg-foreground/70 align-baseline"
            />
          )}
        </div>
      )}

      {status === 'error' && error && (
        <div className="mt-3 flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  )
}
