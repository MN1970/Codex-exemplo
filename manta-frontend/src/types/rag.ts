/**
 * types/rag.ts — Tipos do domínio RAG (Knowledge Hub + busca semântica).
 * Espelham os schemas Pydantic de `manta-backend/routers/rag.py`.
 */

/** Uma coleção RAG/agente vertical (saneamento, energia, portos, ...). */
export interface RagCollection {
  name: string
  storage_prefix: string
  sources: string
  status: string
}

/** Um card de resultado de busca semântica (POST /rag/search). */
export interface RagSearchResult {
  chunk_id: number
  document_id: string | null
  title: string
  /** Trecho truncado (busca) OU conteúdo completo (GET /rag/chunks/{id}). */
  snippet: string
  /** Similaridade de cosseno normalizada (0–1, quanto maior mais relevante). */
  score: number
  /** Coleção/agente dono do chunk (ex.: "saneamento"). */
  agent: string
  /** Nome do arquivo de origem (ou texto indicando chunk sem documento). */
  source: string
  file_type: string | null
  created_at: string | null
}

/** Um documento indexado no Knowledge Hub (GET/POST/DELETE /rag/documents). */
export interface RagDocument {
  id: string
  collection: string
  title: string
  filename: string
  file_type: string
  source: string
  size_bytes: number
  chunk_count: number
  created_at: string
}

export interface RagSearchParams {
  query: string
  collection?: string | null
  top_k?: number
}

export interface RagDocumentFilters {
  collection?: string | null
  file_type?: string | null
  date_from?: string | null
  date_to?: string | null
  q?: string | null
}
