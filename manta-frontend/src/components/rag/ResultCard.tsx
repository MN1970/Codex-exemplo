import { Calendar, FileText } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import type { RagSearchResult } from '@/types/rag'

interface ResultCardProps {
  result: RagSearchResult
  onOpen: (result: RagSearchResult) => void
}

const AGENT_LABELS: Record<string, string> = {
  saneamento: 'Saneamento (S8)',
  energia: 'Energia (S9)',
  portos: 'Portos (S6)',
  aeroportos: 'Aeroportos (S7)',
  barragens: 'Barragens (S10)',
}

function formatDate(iso: string | null): string | null {
  if (!iso) return null
  try {
    return new Date(iso).toLocaleDateString('pt-BR')
  } catch {
    return null
  }
}

/** Score → cor da barra de similaridade (verde alto, âmbar médio, cinza baixo). */
function scoreTone(score: number): string {
  if (score >= 0.75) return 'bg-emerald-500'
  if (score >= 0.5) return 'bg-amber-500'
  return 'bg-muted-foreground/50'
}

/** Card de um resultado de busca semântica: título, snippet, score, agente e fonte. */
export function ResultCard({ result, onOpen }: ResultCardProps) {
  const scorePct = Math.max(0, Math.min(1, result.score)) * 100
  const date = formatDate(result.created_at)

  return (
    <Card
      role="button"
      tabIndex={0}
      onClick={() => onOpen(result)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onOpen(result)
        }
      }}
      className="cursor-pointer p-4 transition-colors hover:border-primary/50 hover:bg-accent/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="line-clamp-1 text-sm font-semibold leading-tight">{result.title}</h3>
        <span className="shrink-0 rounded-full bg-secondary px-2 py-0.5 text-[11px] font-medium text-secondary-foreground">
          {AGENT_LABELS[result.agent] ?? result.agent}
        </span>
      </div>

      <p className="mt-2 line-clamp-3 text-sm text-muted-foreground">{result.snippet}</p>

      <div className="mt-3 flex items-center gap-3">
        <div className="flex flex-1 items-center gap-2">
          <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-muted">
            <div
              className={cn('h-full rounded-full', scoreTone(result.score))}
              style={{ width: `${scorePct}%` }}
            />
          </div>
          <span className="w-10 shrink-0 text-right text-[11px] tabular-nums text-muted-foreground">
            {scorePct.toFixed(0)}%
          </span>
        </div>
      </div>

      <div className="mt-2 flex items-center gap-3 text-[11px] text-muted-foreground">
        <span className="flex min-w-0 items-center gap-1">
          <FileText className="h-3 w-3 shrink-0" />
          <span className="truncate">{result.source}</span>
        </span>
        {date && (
          <span className="flex shrink-0 items-center gap-1">
            <Calendar className="h-3 w-3" />
            {date}
          </span>
        )}
      </div>
    </Card>
  )
}
