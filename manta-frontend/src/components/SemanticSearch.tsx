import { useCallback, useMemo, useState } from 'react'
import { ChevronRight, Loader2, Search } from 'lucide-react'
import { useSemanticSearch } from '@/hooks/useSemanticSearch'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card } from '@/components/ui/card'

interface SemanticSearchProps {
  onResultSelect?: (result: SearchHit) => void
  defaultCollection?: string
  maxResults?: number
  placeholder?: string
}

export interface SearchHit {
  chunk_id: number
  content: string
  score: number
  document_id?: string
  document_title?: string
  document_filename?: string
  file_type?: string
  collection: string
}

/**
 * Componente de busca semântica com debouncing automático (300ms).
 *
 * Features:
 * - Input debounced (300ms) para evitar múltiplas requisições
 * - Spinner de loading enquanto busca
 * - Cards de resultados com score de relevância
 * - Evento onResultSelect para integração com outros componentes
 * - Cache de buscas recentes (5 min TTL)
 * - Suporte a filtro por coleção (opcional)
 */
export function SemanticSearch({
  onResultSelect,
  defaultCollection,
  maxResults = 10,
  placeholder = 'Buscar documentos com IA...',
}: SemanticSearchProps) {
  const [query, setQuery] = useState('')
  const [selectedCollection, setSelectedCollection] = useState(defaultCollection || '')

  // Usar hook com debounce automático
  const { results, isLoading, error, isCached } = useSemanticSearch(query, {
    limit: maxResults,
    collection: selectedCollection || undefined,
    debounceMs: 300,
  })

  const handleResultClick = useCallback(
    (result: SearchHit) => {
      onResultSelect?.(result)
    },
    [onResultSelect],
  )

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.currentTarget.value)
  }, [])

  // Snippets truncados dos resultados
  const displayResults = useMemo(() => {
    return results.slice(0, maxResults).map((hit) => ({
      ...hit,
      snippet: _truncateText(hit.content, 150),
      scorePercent: Math.round(hit.score * 100),
    }))
  }, [results, maxResults])

  const hasResults = displayResults.length > 0
  const showLoading = isLoading && query.trim().length > 0

  return (
    <div className="w-full space-y-4">
      {/* Input com ícone de busca */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <Input
          type="text"
          placeholder={placeholder}
          value={query}
          onChange={handleSearchChange}
          className="pl-10 pr-4 py-2"
          autoFocus
        />
      </div>

      {/* Filtro por coleção (opcional) */}
      {/* Pode ser customizado conforme necessário */}

      {/* Estado vazio */}
      {!query.trim() && !hasResults && (
        <div className="rounded-lg border border-dashed border-gray-200 p-8 text-center">
          <p className="text-sm text-gray-500">
            Digite um termo para buscar em documentos técnicos
          </p>
        </div>
      )}

      {/* Spinner de loading */}
      {showLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
          <span className="ml-2 text-sm text-gray-600">Buscando...</span>
        </div>
      )}

      {/* Erro */}
      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Resultados */}
      {hasResults && (
        <div className="space-y-3">
          <div className="text-xs text-gray-500">
            {results.length} resultado{results.length !== 1 ? 's' : ''} encontrado
            {isCached && ' (em cache)'}
          </div>

          {displayResults.map((hit) => (
            <SearchResultCard
              key={hit.chunk_id}
              hit={hit}
              scorePercent={hit.scorePercent}
              snippet={hit.snippet}
              onClick={() => handleResultClick(hit)}
            />
          ))}
        </div>
      )}

      {/* Nenhum resultado */}
      {query.trim() && !showLoading && !hasResults && !error && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
          <p className="text-sm text-yellow-700">
            Nenhum resultado encontrado para "{query}"
          </p>
        </div>
      )}
    </div>
  )
}

/**
 * Card de resultado individual com score de relevância.
 */
function SearchResultCard({
  hit,
  scorePercent,
  snippet,
  onClick,
}: {
  hit: SearchHit
  scorePercent: number
  snippet: string
  onClick: () => void
}) {
  return (
    <Card
      className="cursor-pointer transition-colors hover:bg-gray-50"
      onClick={onClick}
    >
      <div className="space-y-2 p-4">
        {/* Título + Score */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-sm truncate text-gray-900">
              {hit.document_title || hit.document_filename || `Chunk #${hit.chunk_id}`}
            </h3>
            <p className="text-xs text-gray-500 mt-1">
              {hit.collection}
              {hit.file_type && ` • ${hit.file_type.toUpperCase()}`}
            </p>
          </div>

          {/* Score badge */}
          <div className="flex flex-col items-end gap-2">
            <div
              className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold ${_scoreColor(scorePercent)}`}
            >
              {scorePercent}%
            </div>
            <ChevronRight className="h-4 w-4 text-gray-400" />
          </div>
        </div>

        {/* Snippet */}
        <p className="text-xs text-gray-600 leading-relaxed">{snippet}</p>
      </div>
    </Card>
  )
}

/**
 * Cores do score de relevância.
 */
function _scoreColor(percent: number): string {
  if (percent >= 80) return 'bg-green-100 text-green-800'
  if (percent >= 60) return 'bg-blue-100 text-blue-800'
  if (percent >= 40) return 'bg-yellow-100 text-yellow-800'
  return 'bg-gray-100 text-gray-800'
}

/**
 * Trunca texto a comprimento máximo, adicionando "..." se truncado.
 */
function _truncateText(text: string, maxLength: number): string {
  const clean = text.replace(/\s+/g, ' ').trim()
  if (clean.length <= maxLength) return clean
  return clean.substring(0, maxLength).trim() + '…'
}
