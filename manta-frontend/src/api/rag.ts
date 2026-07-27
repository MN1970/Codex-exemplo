import { apiClient } from '@/api/client'
import type {
  RagCollection,
  RagDocument,
  RagDocumentFilters,
  RagSearchParams,
  RagSearchResult,
} from '@/types/rag'

/** GET /rag/collections — coleções/agentes verticais com RAG dedicado. */
export async function listCollections(): Promise<RagCollection[]> {
  const { data } = await apiClient.get<RagCollection[]>('/rag/collections')
  return data
}

/**
 * POST /rag/search — busca semântica "rica": cards com título, snippet,
 * score, agente e fonte. `collection` omitido/null busca em todas.
 */
export async function searchRag(
  params: RagSearchParams,
  signal?: AbortSignal,
): Promise<RagSearchResult[]> {
  const { data } = await apiClient.post<RagSearchResult[]>(
    '/rag/search',
    {
      query: params.query,
      collection: params.collection ?? null,
      top_k: params.top_k ?? 10,
    },
    { signal },
  )
  return data
}

/** GET /rag/chunks/{id} — conteúdo completo de um chunk (ChunkViewer). */
export async function getChunk(chunkId: number): Promise<RagSearchResult> {
  const { data } = await apiClient.get<RagSearchResult>(`/rag/chunks/${chunkId}`)
  return data
}

/**
 * POST /rag/upload — envia um arquivo (PDF/txt/md) para indexação:
 * extrai texto, faz chunking e gera embeddings no backend.
 */
export async function uploadDocument(
  file: File,
  collection: string,
  title?: string,
  onProgress?: (percent: number) => void,
): Promise<RagDocument> {
  const form = new FormData()
  form.append('file', file)
  form.append('collection', collection)
  if (title) form.append('title', title)

  const { data } = await apiClient.post<RagDocument>('/rag/upload', form, {
    // Content-Type explicitamente indefinido: deixa o axios detectar
    // FormData e gerar o boundary do multipart sozinho — o header
    // default 'application/json' da instância (api/client.ts) atrapalharia.
    headers: { 'Content-Type': undefined },
    onUploadProgress: (evt) => {
      if (!onProgress || !evt.total) return
      onProgress(Math.round((evt.loaded / evt.total) * 100))
    },
  })
  return data
}

/** GET /rag/documents — lista documentos com filtros (agente/tipo/período/texto). */
export async function listDocuments(filters: RagDocumentFilters = {}): Promise<RagDocument[]> {
  const { data } = await apiClient.get<RagDocument[]>('/rag/documents', {
    params: {
      collection: filters.collection || undefined,
      file_type: filters.file_type || undefined,
      date_from: filters.date_from || undefined,
      date_to: filters.date_to || undefined,
      q: filters.q || undefined,
    },
  })
  return data
}

/** DELETE /rag/documents/{id} — remove o documento e seus chunks (cascade). */
export async function deleteDocument(documentId: string): Promise<void> {
  await apiClient.delete(`/rag/documents/${documentId}`)
}
