import { useCallback, useEffect, useRef, useState } from 'react'
import { apiClient } from '@/api/client'

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

export interface SearchResponse {
  query: string
  collection?: string
  total_hits: number
  results: SearchHit[]
  took_ms: number
}

interface UseSemanticSearchOptions {
  limit?: number
  collection?: string
  debounceMs?: number
  cacheTtlMs?: number
}

interface CacheEntry {
  timestamp: number
  data: SearchResponse
}

// Cache global de buscas (5 min TTL por padrão)
const searchCache = new Map<string, CacheEntry>()

/**
 * Hook para busca semântica com debouncing e caching automático.
 *
 * Features:
 * - Debounce configurável (padrão 300ms) para evitar requisições excessivas
 * - Cache de 5 min por padrão (TTL), evita buscas repetidas
 * - Loading state automático
 * - Error handling com mensagens amigáveis
 * - Chave de cache baseada em (query, collection, limit)
 *
 * @param query - Texto de busca (vazio = sem buscar)
 * @param options - Opções (limit, collection, debounceMs, cacheTtlMs)
 *
 * @returns { results, isLoading, error, isCached }
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const [query, setQuery] = useState('')
 *   const { results, isLoading } = useSemanticSearch(query, {
 *     limit: 10,
 *     collection: 'saneamento',
 *     debounceMs: 300,
 *   })
 *
 *   return (
 *     <>
 *       <input value={query} onChange={(e) => setQuery(e.target.value)} />
 *       {isLoading && <Spinner />}
 *       {results.map((hit) => <ResultCard key={hit.chunk_id} hit={hit} />)}
 *     </>
 *   )
 * }
 * ```
 */
export function useSemanticSearch(
  query: string,
  options: UseSemanticSearchOptions = {},
): {
  results: SearchHit[]
  isLoading: boolean
  error: string | null
  isCached: boolean
} {
  const {
    limit = 10,
    collection,
    debounceMs = 300,
    cacheTtlMs = 5 * 60 * 1000, // 5 min padrão
  } = options

  const [results, setResults] = useState<SearchHit[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isCached, setIsCached] = useState(false)

  // Refs para debouncing
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null)
  const lastQueryRef = useRef('')

  // Gera chave de cache determinística
  const getCacheKey = useCallback(
    (q: string, col?: string, lim?: number): string => {
      return `search:${q}:${col || 'all'}:${lim || 10}`
    },
    [],
  )

  // Limpa cache expirado
  const _cleanExpiredCache = useCallback(() => {
    const now = Date.now()
    for (const [key, entry] of searchCache.entries()) {
      if (now - entry.timestamp > cacheTtlMs) {
        searchCache.delete(key)
      }
    }
  }, [cacheTtlMs])

  // Busca na API
  const _fetchResults = useCallback(
    async (q: string) => {
      if (!q.trim()) {
        setResults([])
        setError(null)
        setIsCached(false)
        return
      }

      const cacheKey = getCacheKey(q, collection, limit)

      // Limpa cache expirado
      _cleanExpiredCache()

      // Verifica cache
      if (searchCache.has(cacheKey)) {
        const cached = searchCache.get(cacheKey)!
        setResults(cached.data.results)
        setError(null)
        setIsCached(true)
        setIsLoading(false)
        return
      }

      setIsLoading(true)
      setError(null)
      setIsCached(false)

      try {
        const params: Record<string, string | number> = {
          q,
          limit,
        }
        if (collection) {
          params.collection = collection
        }

        const response = await apiClient.get<SearchResponse>('/search', {
          params,
          timeout: 15_000,
        })

        const { data } = response
        setResults(data.results)

        // Armazena no cache
        searchCache.set(cacheKey, {
          timestamp: Date.now(),
          data,
        })
      } catch (err) {
        const message =
          err instanceof Error
            ? err.message
            : 'Erro ao buscar. Tente novamente.'
        setError(message)
        setResults([])
      } finally {
        setIsLoading(false)
      }
    },
    [collection, limit, getCacheKey, _cleanExpiredCache],
  )

  // Debounce da busca
  useEffect(() => {
    // Se query está vazia, limpa tudo imediatamente
    if (!query.trim()) {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
      setResults([])
      setError(null)
      setIsCached(false)
      lastQueryRef.current = ''
      return
    }

    // Se query é idêntica à última, não faz nada
    if (query === lastQueryRef.current) {
      return
    }

    lastQueryRef.current = query

    // Cancela timer anterior e cria novo
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }

    setIsLoading(true)

    debounceTimerRef.current = setTimeout(() => {
      _fetchResults(query)
    }, debounceMs)

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [query, debounceMs, _fetchResults])

  return { results, isLoading, error, isCached }
}
