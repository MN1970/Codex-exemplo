import { useEffect, useMemo, useState } from 'react'
import { AlertCircle, FileSearch, Sparkles } from 'lucide-react'
import { listCollections, searchRag } from '@/api/rag'
import { useDebouncedValue } from '@/hooks/useDebouncedValue'
import type { RagCollection, RagSearchResult } from '@/types/rag'
import { SearchInput } from '@/components/rag/SearchInput'
import { ResultCard } from '@/components/rag/ResultCard'
import { ChunkViewer } from '@/components/rag/ChunkViewer'
import { cn } from '@/lib/utils'

const AGENT_LABELS: Record<string, string> = {
  saneamento: 'Saneamento (S8)',
  energia: 'Energia (S9)',
  portos: 'Portos (S6)',
  aeroportos: 'Aeroportos (S7)',
  barragens: 'Barragens (S10)',
}

interface RAGSearchProps {
  /** Pre-selects a collection/agent and hides the picker — for embedding
   *  RAGSearch scoped to a single agent's knowledge base. */
  fixedCollection?: string
  /** Extra classes on the root element. */
  className?: string
}

/**
 * Semantic search over the RAG knowledge base: debounced input →
 * POST /rag/search → result cards (title, snippet, similarity score,
 * agent, source). Clicking a card opens the full chunk in a modal.
 */
export function RAGSearch({ fixedCollection, className }: RAGSearchProps) {
  const [query, setQuery] = useState('')
  const [collection, setCollection] = useState<string>(fixedCollection ?? 'all')
  const [collections, setCollections] = useState<RagCollection[]>([])
  const [results, setResults] = useState<RagSearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<RagSearchResult | null>(null)
  const [hasSearched, setHasSearched] = useState(false)

  const debouncedQuery = useDebouncedValue(query.trim(), 350)

  useEffect(() => {
    if (fixedCollection) return
    listCollections()
      .then(setCollections)
      .catch(() => setCollections([]))
  }, [fixedCollection])

  useEffect(() => {
    const controller = new AbortController()

    async function run() {
      if (!debouncedQuery) {
        setResults([])
        setError(null)
        setIsLoading(false)
        setHasSearched(false)
        return
      }

      setIsLoading(true)
      setError(null)

      try {
        const data = await searchRag(
          {
            query: debouncedQuery,
            collection: collection === 'all' ? null : collection,
            top_k: 12,
          },
          controller.signal,
        )
        if (controller.signal.aborted) return
        setResults(data)
        setHasSearched(true)
      } catch (err: unknown) {
        if (controller.signal.aborted) return
        setResults([])
        setHasSearched(true)
        const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        setError(typeof detail === 'string' ? detail : 'Falha ao buscar na base de conhecimento.')
      } finally {
        if (!controller.signal.aborted) setIsLoading(false)
      }
    }

    void run()
    return () => controller.abort()
  }, [debouncedQuery, collection])

  const emptyState = useMemo(() => {
    if (isLoading) return null
    if (!debouncedQuery) {
      return {
        icon: Sparkles,
        title: 'Busque na base de conhecimento',
        detail: 'Digite um termo para buscar por similaridade semântica nos documentos indexados.',
      }
    }
    if (hasSearched && !error && results.length === 0) {
      return {
        icon: FileSearch,
        title: 'Nenhum resultado encontrado',
        detail: `Nada relevante para "${debouncedQuery}" nesta coleção. Tente outros termos ou mude o filtro de agente.`,
      }
    }
    return null
  }, [isLoading, debouncedQuery, hasSearched, error, results.length])

  return (
    <div className={cn('flex flex-col gap-4', className)}>
      <div className="flex flex-col gap-3 sm:flex-row">
        <SearchInput value={query} onChange={setQuery} isLoading={isLoading} className="flex-1" />
        {!fixedCollection && (
          <select
            value={collection}
            onChange={(e) => setCollection(e.target.value)}
            aria-label="Filtrar por agente"
            className="h-11 rounded-md border border-input bg-transparent px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
          >
            <option value="all">Todos os agentes</option>
            {collections.map((c) => (
              <option key={c.name} value={c.name}>
                {AGENT_LABELS[c.name] ?? c.name}
              </option>
            ))}
          </select>
        )}
      </div>

      {error && (
        <div className="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          {error}
        </div>
      )}

      {emptyState && (
        <div className="flex flex-col items-center gap-2 rounded-lg border border-dashed border-border py-12 text-center text-muted-foreground">
          <emptyState.icon className="h-8 w-8" />
          <p className="text-sm font-medium text-foreground">{emptyState.title}</p>
          <p className="max-w-sm text-xs">{emptyState.detail}</p>
        </div>
      )}

      {results.length > 0 && (
        <div className="grid gap-3 sm:grid-cols-2">
          {results.map((result) => (
            <ResultCard key={result.chunk_id} result={result} onOpen={setSelected} />
          ))}
        </div>
      )}

      <ChunkViewer result={selected} onClose={() => setSelected(null)} />
    </div>
  )
}
