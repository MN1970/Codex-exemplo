import { useCallback, useEffect, useRef, useState } from 'react'
import {
  AlertCircle,
  FileText,
  Loader2,
  Search as SearchIcon,
  Trash2,
  UploadCloud,
} from 'lucide-react'
import { deleteDocument, listCollections, listDocuments, uploadDocument } from '@/api/rag'
import { useDebouncedValue } from '@/hooks/useDebouncedValue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { RAGSearch } from '@/components/rag/RAGSearch'
import { cn } from '@/lib/utils'
import type { RagCollection, RagDocument } from '@/types/rag'

const AGENT_LABELS: Record<string, string> = {
  saneamento: 'Saneamento (S8)',
  energia: 'Energia (S9)',
  portos: 'Portos (S6)',
  aeroportos: 'Aeroportos (S7)',
  barragens: 'Barragens (S10)',
}

interface UploadItem {
  id: string
  file: File
  status: 'uploading' | 'done' | 'error'
  progress: number
  error?: string
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  const units = ['KB', 'MB', 'GB']
  let value = bytes / 1024
  let unitIndex = 0
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024
    unitIndex += 1
  }
  return `${value.toFixed(1)} ${units[unitIndex]}`
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
  } catch {
    return iso
  }
}

export function KnowledgeHub() {
  const [tab, setTab] = useState<'documents' | 'search'>('documents')

  // --- Coleções/agentes ---------------------------------------------------
  const [collections, setCollections] = useState<RagCollection[]>([])
  const [uploadCollection, setUploadCollection] = useState<string>('')

  // --- Upload (drag-drop) ---------------------------------------------------
  const [isDragging, setIsDragging] = useState(false)
  const [uploads, setUploads] = useState<UploadItem[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  // --- Documentos (lista + filtros) -----------------------------------------
  const [documents, setDocuments] = useState<RagDocument[]>([])
  const [isLoadingDocs, setIsLoadingDocs] = useState(false)
  const [docsError, setDocsError] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const [filterCollection, setFilterCollection] = useState('all')
  const [filterType, setFilterType] = useState('all')
  const [filterDateFrom, setFilterDateFrom] = useState('')
  const [filterDateTo, setFilterDateTo] = useState('')
  const [filterQuery, setFilterQuery] = useState('')
  const debouncedFilterQuery = useDebouncedValue(filterQuery, 300)

  useEffect(() => {
    document.title = 'Manta Frontend — Knowledge Hub'
    listCollections()
      .then((data) => {
        setCollections(data)
        setUploadCollection((prev) => prev || data[0]?.name || '')
      })
      .catch(() => setCollections([]))
  }, [])

  const fetchDocuments = useCallback(async () => {
    setIsLoadingDocs(true)
    setDocsError(null)
    try {
      const data = await listDocuments({
        collection: filterCollection === 'all' ? null : filterCollection,
        file_type: filterType === 'all' ? null : filterType,
        date_from: filterDateFrom || null,
        date_to: filterDateTo || null,
        q: debouncedFilterQuery || null,
      })
      setDocuments(data)
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setDocsError(detail || 'Falha ao carregar documentos.')
    } finally {
      setIsLoadingDocs(false)
    }
  }, [filterCollection, filterType, filterDateFrom, filterDateTo, debouncedFilterQuery])

  useEffect(() => {
    async function run() {
      await fetchDocuments()
    }
    void run()
  }, [fetchDocuments])

  // --- Upload handlers -------------------------------------------------------
  const handleFiles = useCallback(
    (fileList: FileList | File[]) => {
      const files = Array.from(fileList)
      if (files.length === 0) return
      if (!uploadCollection) {
        setUploads((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            file: files[0],
            status: 'error',
            progress: 0,
            error: 'Selecione um agente de destino antes de enviar.',
          },
        ])
        return
      }

      for (const file of files) {
        const id = crypto.randomUUID()
        setUploads((prev) => [...prev, { id, file, status: 'uploading', progress: 0 }])

        uploadDocument(file, uploadCollection, undefined, (percent) => {
          setUploads((prev) => prev.map((u) => (u.id === id ? { ...u, progress: percent } : u)))
        })
          .then(() => {
            setUploads((prev) => prev.map((u) => (u.id === id ? { ...u, status: 'done', progress: 100 } : u)))
            fetchDocuments()
          })
          .catch((err) => {
            const detail = err?.response?.data?.detail
            setUploads((prev) =>
              prev.map((u) =>
                u.id === id
                  ? { ...u, status: 'error', error: typeof detail === 'string' ? detail : 'Falha no upload.' }
                  : u,
              ),
            )
          })
      }
    },
    [uploadCollection, fetchDocuments],
  )

  function handleDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files?.length) handleFiles(e.dataTransfer.files)
  }

  async function handleDelete(doc: RagDocument) {
    if (!window.confirm(`Remover "${doc.title}"? Isso apaga o documento e todos os seus chunks indexados.`)) {
      return
    }
    setDeletingId(doc.id)
    try {
      await deleteDocument(doc.id)
      setDocuments((prev) => prev.filter((d) => d.id !== doc.id))
    } catch {
      setDocsError('Falha ao remover o documento. Tente novamente.')
    } finally {
      setDeletingId(null)
    }
  }

  const fileTypeOptions = Array.from(new Set(documents.map((d) => d.file_type).filter(Boolean)))

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Knowledge Hub</h1>
        <p className="mt-1 text-muted-foreground">
          Base de conhecimento RAG dos agentes verticais — envie documentos, gerencie o
          índice e busque por similaridade semântica.
        </p>
      </div>

      <div className="flex gap-1 border-b border-border">
        <button
          type="button"
          onClick={() => setTab('documents')}
          className={cn(
            'border-b-2 px-3 py-2 text-sm font-medium transition-colors',
            tab === 'documents'
              ? 'border-primary text-foreground'
              : 'border-transparent text-muted-foreground hover:text-foreground',
          )}
        >
          Documentos
        </button>
        <button
          type="button"
          onClick={() => setTab('search')}
          className={cn(
            'border-b-2 px-3 py-2 text-sm font-medium transition-colors',
            tab === 'search'
              ? 'border-primary text-foreground'
              : 'border-transparent text-muted-foreground hover:text-foreground',
          )}
        >
          Buscar
        </button>
      </div>

      {tab === 'search' && <RAGSearch />}

      {tab === 'documents' && (
        <div className="flex flex-col gap-6">
          {/* --- Upload --- */}
          <Card>
            <CardHeader>
              <CardTitle>Enviar documentos</CardTitle>
              <CardDescription>PDF, TXT ou Markdown — o texto é extraído, dividido em chunks e indexado com embeddings.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="flex flex-col gap-2 sm:w-64">
                <label htmlFor="upload-collection" className="text-sm font-medium">
                  Agente de destino
                </label>
                <select
                  id="upload-collection"
                  value={uploadCollection}
                  onChange={(e) => setUploadCollection(e.target.value)}
                  className="h-10 rounded-md border border-input bg-transparent px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  {collections.map((c) => (
                    <option key={c.name} value={c.name}>
                      {AGENT_LABELS[c.name] ?? c.name}
                    </option>
                  ))}
                </select>
              </div>

              <div
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => {
                  e.preventDefault()
                  setIsDragging(true)
                }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                role="button"
                tabIndex={0}
                className={cn(
                  'flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed p-8 text-center transition-colors',
                  isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/40',
                )}
              >
                <UploadCloud className="h-8 w-8 text-muted-foreground" />
                <p className="text-sm font-medium">Arraste arquivos aqui ou clique para selecionar</p>
                <p className="text-xs text-muted-foreground">PDF, TXT, MD — múltiplos arquivos são aceitos</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files) handleFiles(e.target.files)
                    e.target.value = ''
                  }}
                />
              </div>

              {uploads.length > 0 && (
                <ul className="flex flex-col gap-2">
                  {uploads.map((u) => (
                    <li
                      key={u.id}
                      className="flex items-center gap-3 rounded-md border border-border px-3 py-2 text-sm"
                    >
                      <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
                      <span className="min-w-0 flex-1 truncate">{u.file.name}</span>
                      {u.status === 'uploading' && (
                        <span className="flex shrink-0 items-center gap-2 text-xs text-muted-foreground">
                          <Loader2 className="h-3.5 w-3.5 animate-spin" />
                          {u.progress}%
                        </span>
                      )}
                      {u.status === 'done' && (
                        <span className="shrink-0 text-xs font-medium text-emerald-600 dark:text-emerald-400">
                          Indexado
                        </span>
                      )}
                      {u.status === 'error' && (
                        <span className="flex shrink-0 items-center gap-1 text-xs text-destructive">
                          <AlertCircle className="h-3.5 w-3.5" />
                          {u.error}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          {/* --- Filtros --- */}
          <Card>
            <CardHeader>
              <CardTitle>Documentos indexados</CardTitle>
              <CardDescription>Filtre por agente, tipo de arquivo e período.</CardDescription>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                <div className="relative lg:col-span-2">
                  <SearchIcon className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    value={filterQuery}
                    onChange={(e) => setFilterQuery(e.target.value)}
                    placeholder="Filtrar por título ou nome do arquivo…"
                    className="pl-8"
                  />
                </div>
                <select
                  value={filterCollection}
                  onChange={(e) => setFilterCollection(e.target.value)}
                  aria-label="Filtrar por agente"
                  className="h-10 rounded-md border border-input bg-transparent px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="all">Todos os agentes</option>
                  {collections.map((c) => (
                    <option key={c.name} value={c.name}>
                      {AGENT_LABELS[c.name] ?? c.name}
                    </option>
                  ))}
                </select>
                <select
                  value={filterType}
                  onChange={(e) => setFilterType(e.target.value)}
                  aria-label="Filtrar por tipo de arquivo"
                  className="h-10 rounded-md border border-input bg-transparent px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="all">Todos os tipos</option>
                  {fileTypeOptions.map((ft) => (
                    <option key={ft} value={ft}>
                      {ft.toUpperCase()}
                    </option>
                  ))}
                </select>
                <Input
                  type="date"
                  value={filterDateFrom}
                  onChange={(e) => setFilterDateFrom(e.target.value)}
                  aria-label="Data inicial"
                />
                <Input
                  type="date"
                  value={filterDateTo}
                  onChange={(e) => setFilterDateTo(e.target.value)}
                  aria-label="Data final"
                />
              </div>

              {docsError && (
                <div className="flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 p-3 text-sm text-destructive">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                  {docsError}
                </div>
              )}

              {isLoadingDocs ? (
                <div className="flex items-center gap-2 py-8 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Carregando documentos…
                </div>
              ) : documents.length === 0 ? (
                <div className="flex flex-col items-center gap-1 py-10 text-center text-muted-foreground">
                  <FileText className="h-8 w-8" />
                  <p className="text-sm font-medium text-foreground">Nenhum documento encontrado</p>
                  <p className="text-xs">Envie um arquivo acima ou ajuste os filtros.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-border text-xs uppercase tracking-wide text-muted-foreground">
                        <th className="py-2 pr-3 font-medium">Título</th>
                        <th className="py-2 pr-3 font-medium">Agente</th>
                        <th className="py-2 pr-3 font-medium">Tipo</th>
                        <th className="py-2 pr-3 font-medium">Tamanho</th>
                        <th className="py-2 pr-3 font-medium">Chunks</th>
                        <th className="py-2 pr-3 font-medium">Data</th>
                        <th className="py-2 pr-3 font-medium text-right">Ações</th>
                      </tr>
                    </thead>
                    <tbody>
                      {documents.map((doc) => (
                        <tr key={doc.id} className="border-b border-border/60 last:border-0">
                          <td className="max-w-xs truncate py-2 pr-3 font-medium" title={doc.title}>
                            {doc.title}
                          </td>
                          <td className="py-2 pr-3">
                            <span className="rounded-full bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground">
                              {AGENT_LABELS[doc.collection] ?? doc.collection}
                            </span>
                          </td>
                          <td className="py-2 pr-3 uppercase text-muted-foreground">{doc.file_type}</td>
                          <td className="py-2 pr-3 text-muted-foreground">{formatBytes(doc.size_bytes)}</td>
                          <td className="py-2 pr-3 text-muted-foreground">{doc.chunk_count}</td>
                          <td className="py-2 pr-3 text-muted-foreground">{formatDate(doc.created_at)}</td>
                          <td className="py-2 pr-3 text-right">
                            <Button
                              variant="ghost"
                              size="icon"
                              disabled={deletingId === doc.id}
                              onClick={() => handleDelete(doc)}
                              aria-label={`Remover ${doc.title}`}
                            >
                              {deletingId === doc.id ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <Trash2 className="h-4 w-4 text-destructive" />
                              )}
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
