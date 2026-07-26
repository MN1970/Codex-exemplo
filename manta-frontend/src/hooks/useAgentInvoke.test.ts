import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { useAgentInvoke } from '@/hooks/useAgentInvoke'
import * as agentsApi from '@/api/agents'
import type { InvokeStreamHandlers } from '@/api/agents'

vi.mock('@/api/agents', () => ({
  invokeAgentStream: vi.fn(),
}))

const mockedInvokeStream = vi.mocked(agentsApi.invokeAgentStream)

afterEach(() => {
  mockedInvokeStream.mockReset()
})

describe('useAgentInvoke', () => {
  it('starts idle', () => {
    const { result } = renderHook(() => useAgentInvoke())
    expect(result.current.status).toBe('idle')
    expect(result.current.content).toBe('')
    expect(result.current.error).toBeNull()
  })

  it('streams meta/chunk/done into state, ending in "done"', async () => {
    mockedInvokeStream.mockImplementation(
      async (_slug, _prompt, handlers: InvokeStreamHandlers) => {
        handlers.onMeta?.({ session_id: 's-1', agent_slug: 'maestro', agent_code: 'Manta 00' })
        handlers.onChunk?.('Olá ')
        handlers.onChunk?.('mundo')
        handlers.onDone?.({ session_id: 's-1', full_response: 'Olá mundo' })
      },
    )

    const { result } = renderHook(() => useAgentInvoke())

    await act(async () => {
      await result.current.invoke('maestro', 'oi')
    })

    expect(result.current.status).toBe('done')
    expect(result.current.content).toBe('Olá mundo')
    expect(result.current.sessionId).toBe('s-1')
  })

  it('moves to "error" and keeps the message when the stream rejects', async () => {
    mockedInvokeStream.mockRejectedValue(new Error('boom'))

    const { result } = renderHook(() => useAgentInvoke())

    await act(async () => {
      await result.current.invoke('maestro', 'oi')
    })

    expect(result.current.status).toBe('error')
    expect(result.current.error).toBe('boom')
  })

  it('reset() clears content/error/session back to idle', async () => {
    mockedInvokeStream.mockRejectedValue(new Error('boom'))
    const { result } = renderHook(() => useAgentInvoke())

    await act(async () => {
      await result.current.invoke('maestro', 'oi')
    })
    expect(result.current.status).toBe('error')

    act(() => {
      result.current.reset()
    })

    expect(result.current.status).toBe('idle')
    expect(result.current.content).toBe('')
    expect(result.current.error).toBeNull()
    expect(result.current.sessionId).toBeNull()
  })

  it('cancel() aborts the in-flight signal and returns to idle without setting an error', async () => {
    let capturedSignal: AbortSignal | undefined
    mockedInvokeStream.mockImplementation(async (_slug, _prompt, _handlers, signal) => {
      capturedSignal = signal
      // Simulate a fetch that only rejects once the caller aborts it.
      await new Promise((_resolve, reject) => {
        signal?.addEventListener('abort', () => reject(new DOMException('aborted', 'AbortError')))
      })
    })

    const { result } = renderHook(() => useAgentInvoke())

    let invokePromise!: Promise<void>
    act(() => {
      invokePromise = result.current.invoke('maestro', 'oi')
    })

    await waitFor(() => expect(capturedSignal).toBeDefined())
    expect(result.current.status).toBe('streaming')

    act(() => {
      result.current.cancel()
    })

    await act(async () => {
      await invokePromise
    })

    expect(result.current.status).toBe('idle')
    expect(result.current.error).toBeNull()
  })
})
