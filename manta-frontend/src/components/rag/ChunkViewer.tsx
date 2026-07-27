import { useEffect, useState } from 'react'
import { AlertCircle, Loader2, X } from 'lucide-react'
import { getChunk } from '@/api/rag'
import { Button } from '@/components/ui/button'
import type { RagSearchResult } from '@/types/rag'

interface ChunkViewerProps {
  /** Result the user clicked — shown immediately while the full chunk loads. */
  result: RagSearchResult | null
  onClose: () => void
}

const AGENT_LABELS: Record<string, string> = {
  saneamento: 'Saneamento (S8)',
  energia: 'Energia (S9)',
  portos: 'Portos (S6)',
  aeroportos: 'Aeroportos (S7)',
  barragens: 'Barragens (S10)',
}

/**
 * Modal that shows the full content of a chunk (the search card only
 * shows a truncated snippet). Fetches GET /rag/chunks/{id} on open for
 * the untruncated text; falls back to the snippet already in hand if
 * that request fails, so the user never sees an empty modal.
 */
export function ChunkViewer({ result, onClose }: ChunkViewerProps) {
  const [fullText, setFullText] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const isOpen = result !== null

  useEffect(() => {
    if (!result) return
    let cancelled = false

    async function run() {
      if (!result) return
      setFullText(null)
      setError(null)
      setIsLoading(true)
      try {
        const chunk = await getChunk(result.chunk_id)
        if (!cancelled) setFullText(chunk.snippet)
      } catch {
        if (!cancelled) {
          setError('Não foi possível carregar o conteúdo completo — exibindo o trecho da busca.')
        }
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }

    void run()
    return () => {
      cancelled = true
    }
  }, [result])

  useEffect(() => {
    if (!isOpen) return
    document.body.style.overflow = 'hidden'
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => {
      document.body.style.overflow = ''
      window.removeEventListener('keydown', onKeyDown)
    }
  }, [isOpen, onClose])

  if (!result) return null

  const displayText = fullText ?? result.snippet

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-label={result.title}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="flex max-h-[85vh] w-full max-w-2xl flex-col rounded-lg border border-border bg-card text-card-foreground shadow-lg"
      >
        <div className="flex items-start justify-between gap-3 border-b border-border p-4">
          <div className="min-w-0">
            <h2 className="truncate text-base font-semibold">{result.title}</h2>
            <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
              <span className="rounded-full bg-secondary px-2 py-0.5 font-medium text-secondary-foreground">
                {AGENT_LABELS[result.agent] ?? result.agent}
              </span>
              <span>{result.source}</span>
              {result.created_at && (
                <span>{new Date(result.created_at).toLocaleDateString('pt-BR')}</span>
              )}
              <span>similaridade {(Math.max(0, Math.min(1, result.score)) * 100).toFixed(0)}%</span>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label="Fechar">
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="overflow-y-auto p-4">
          {isLoading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              Carregando conteúdo completo…
            </div>
          )}
          {error && (
            <div className="mb-3 flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 p-2 text-xs text-destructive">
              <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              {error}
            </div>
          )}
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{displayText}</p>
        </div>
      </div>
    </div>
  )
}
