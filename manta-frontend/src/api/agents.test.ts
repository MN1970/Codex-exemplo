import MockAdapter from 'axios-mock-adapter'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { apiClient } from '@/api/client'
import { getAgents, invokeAgentStream } from '@/api/agents'
import { useAuthStore } from '@/store/useAuthStore'
import type { Agent } from '@/types/agents'

const sampleAgents: Agent[] = [
  {
    code: 'Manta 00',
    slug: 'maestro',
    name: 'maestro',
    aliases: ['maestro', 'manta-router'],
    tier: 'Haiku→Sonnet',
    status: 'operacional',
    axis: 'horizontal',
  },
]

let mock: MockAdapter

beforeEach(() => {
  mock = new MockAdapter(apiClient)
  useAuthStore.setState({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
  })
})

afterEach(() => {
  mock.restore()
  vi.unstubAllGlobals()
})

describe('getAgents', () => {
  it('GETs /agents and returns the parsed list', async () => {
    mock.onGet('/agents').reply(200, sampleAgents)
    const agents = await getAgents()
    expect(agents).toEqual(sampleAgents)
  })
})

/** Builds a `Response`-like stub whose `.body` streams the given SSE text in chunks. */
function fakeSseResponse(sseText: string, chunkSize = 24): Response {
  const encoder = new TextEncoder()
  const bytes = encoder.encode(sseText)

  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      for (let i = 0; i < bytes.length; i += chunkSize) {
        controller.enqueue(bytes.slice(i, i + chunkSize))
      }
      controller.close()
    },
  })

  return {
    ok: true,
    status: 200,
    body: stream,
    text: async () => sseText,
  } as unknown as Response
}

describe('invokeAgentStream', () => {
  it('parses meta/chunk/done frames split arbitrarily across network chunks', async () => {
    const sse =
      'event: meta\n' +
      'data: {"session_id":"sess-1","agent_slug":"maestro","agent_code":"Manta 00"}\n\n' +
      'event: chunk\n' +
      'data: {"delta":"Olá "}\n\n' +
      'event: chunk\n' +
      'data: {"delta":"mundo"}\n\n' +
      'event: done\n' +
      'data: {"session_id":"sess-1","full_response":"Olá mundo"}\n\n'

    const fetchMock = vi.fn().mockResolvedValue(fakeSseResponse(sse))
    vi.stubGlobal('fetch', fetchMock)

    const onMeta = vi.fn()
    const onChunk = vi.fn()
    const onDone = vi.fn()

    await invokeAgentStream('maestro', 'oi', { onMeta, onChunk, onDone })

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/agents/maestro/invoke'),
      expect.objectContaining({ method: 'POST' }),
    )
    expect(onMeta).toHaveBeenCalledWith({
      session_id: 'sess-1',
      agent_slug: 'maestro',
      agent_code: 'Manta 00',
    })
    expect(onChunk).toHaveBeenNthCalledWith(1, 'Olá ')
    expect(onChunk).toHaveBeenNthCalledWith(2, 'mundo')
    expect(onDone).toHaveBeenCalledWith({
      session_id: 'sess-1',
      full_response: 'Olá mundo',
    })
  })

  it('sends the bearer token from the auth store when present', async () => {
    useAuthStore.getState().setAuth({ accessToken: 'tok-1', refreshToken: 'ref-1' })

    const fetchMock = vi.fn().mockResolvedValue(fakeSseResponse(''))
    vi.stubGlobal('fetch', fetchMock)

    await invokeAgentStream('maestro', 'oi', {})

    const [, init] = fetchMock.mock.calls[0]
    expect((init.headers as Record<string, string>).Authorization).toBe('Bearer tok-1')
  })

  it('throws with the response body when the HTTP call fails', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      body: null,
      text: async () => "Agente 'nao-existe' não encontrado.",
    } as unknown as Response)
    vi.stubGlobal('fetch', fetchMock)

    await expect(invokeAgentStream('nao-existe', 'oi', {})).rejects.toThrow(
      "Agente 'nao-existe' não encontrado.",
    )
  })
})
