import { apiClient } from '@/api/client'
import { env } from '@/lib/env'
import { useAuthStore } from '@/store/useAuthStore'
import type { Agent, InvokeDone, InvokeMeta } from '@/types/agents'

/** GET /agents — the full registry rendered in the Canvas sidebar. */
export async function getAgents(): Promise<Agent[]> {
  const { data } = await apiClient.get<Agent[]>('/agents')
  return data
}

export interface InvokeStreamHandlers {
  onMeta?: (meta: InvokeMeta) => void
  onChunk?: (delta: string) => void
  onDone?: (done: InvokeDone) => void
}

/**
 * POST /agents/{slug}/invoke — streams the agent's reply as Server-Sent
 * Events and resolves once the `done` frame has been received.
 *
 * `EventSource` only supports GET, so a POST-streamed body is read by
 * hand here: `fetch` gives us the raw `ReadableStream`, which we decode
 * and split into SSE frames (`\n\n`-delimited blocks of `event:`/`data:`
 * lines) as bytes arrive.
 */
export async function invokeAgentStream(
  slug: string,
  prompt: string,
  handlers: InvokeStreamHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const token = useAuthStore.getState().accessToken

  const response = await fetch(
    `${env.apiBaseUrl}/agents/${encodeURIComponent(slug)}/invoke`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ prompt }),
      signal,
    },
  )

  if (!response.ok || !response.body) {
    const detail = await response.text().catch(() => '')
    throw new Error(detail || `Falha ao invocar o agente (HTTP ${response.status}).`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  const dispatch = (rawFrame: string) => {
    let eventName = 'message'
    const dataLines: string[] = []

    for (const line of rawFrame.split('\n')) {
      if (line.startsWith('event:')) eventName = line.slice(6).trim()
      else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim())
    }
    if (dataLines.length === 0) return

    let data: unknown
    try {
      data = JSON.parse(dataLines.join('\n'))
    } catch {
      return // malformed frame — drop it rather than crash the stream
    }

    if (eventName === 'meta') handlers.onMeta?.(data as InvokeMeta)
    else if (eventName === 'chunk') {
      handlers.onChunk?.((data as { delta?: string }).delta ?? '')
    } else if (eventName === 'done') handlers.onDone?.(data as InvokeDone)
  }

  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    let boundary = buffer.indexOf('\n\n')
    while (boundary !== -1) {
      dispatch(buffer.slice(0, boundary))
      buffer = buffer.slice(boundary + 2)
      boundary = buffer.indexOf('\n\n')
    }
  }

  if (buffer.trim()) dispatch(buffer)
}
