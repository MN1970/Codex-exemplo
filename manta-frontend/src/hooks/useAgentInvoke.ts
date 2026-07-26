import { useCallback, useEffect, useRef, useState } from 'react'
import { invokeAgentStream } from '@/api/agents'

export type InvokeStatus = 'idle' | 'streaming' | 'done' | 'error'

export interface UseAgentInvokeResult {
  status: InvokeStatus
  content: string
  error: string | null
  sessionId: string | null
  /** Streams a prompt to `POST /agents/{slug}/invoke`; resolves once done. */
  invoke: (slug: string, prompt: string) => Promise<void>
  /** Aborts an in-flight stream (no-op if idle). */
  cancel: () => void
  /** Aborts + clears content/error/session, back to `idle`. */
  reset: () => void
}

/**
 * Drives a single agent invocation: POSTs the prompt, consumes the SSE
 * stream via `invokeAgentStream`, and exposes incrementally-updated
 * state for `<ResponseViewer />` to render.
 */
export function useAgentInvoke(): UseAgentInvokeResult {
  const [status, setStatus] = useState<InvokeStatus>('idle')
  const [content, setContent] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)

  const controllerRef = useRef<AbortController | null>(null)

  const cancel = useCallback(() => {
    controllerRef.current?.abort()
    controllerRef.current = null
    setStatus((prev) => (prev === 'streaming' ? 'idle' : prev))
  }, [])

  const reset = useCallback(() => {
    cancel()
    setStatus('idle')
    setContent('')
    setError(null)
    setSessionId(null)
  }, [cancel])

  const invoke = useCallback(async (slug: string, prompt: string) => {
    // A new invocation supersedes whatever was streaming before.
    controllerRef.current?.abort()
    const controller = new AbortController()
    controllerRef.current = controller

    setStatus('streaming')
    setContent('')
    setError(null)
    setSessionId(null)

    try {
      await invokeAgentStream(
        slug,
        prompt,
        {
          onMeta: (meta) => setSessionId(meta.session_id),
          onChunk: (delta) => setContent((prev) => prev + delta),
          onDone: (done) => {
            setContent(done.full_response)
            setStatus('done')
          },
        },
        controller.signal,
      )
    } catch (err) {
      if (controller.signal.aborted) return // cancel() already reset status
      setStatus('error')
      setError(
        err instanceof Error
          ? err.message
          : 'Erro desconhecido ao invocar o agente.',
      )
    } finally {
      if (controllerRef.current === controller) controllerRef.current = null
    }
  }, [])

  // Abort any in-flight stream if the component unmounts mid-invocation.
  useEffect(() => () => controllerRef.current?.abort(), [])

  return { status, content, error, sessionId, invoke, cancel, reset }
}
