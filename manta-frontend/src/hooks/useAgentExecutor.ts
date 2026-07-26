/**
 * hooks/useAgentExecutor.ts — Hook React para execução de agentes.
 *
 * Conecta a um endpoint SSE POST /executor/{agent_slug}, gerencia streaming
 * de respostas, trata tool_uses, e mantém estado de execução (prompt,
 * resposta, ferramentas, erros).
 */
import { useCallback, useEffect, useRef, useState } from 'react'

export interface ExecutorMessage {
  type: 'meta' | 'chunk' | 'tool_use' | 'tool_result' | 'tool_error' | 'error' | 'done'
  data: Record<string, any>
}

export interface ExecutorState {
  isLoading: boolean
  isStreaming: boolean
  response: string
  error: string | null
  toolCalls: Array<{
    toolName: string
    toolUseId: string
  }>
  sessionId: string | null
  messages: ExecutorMessage[]
}

export interface UseAgentExecutorOptions {
  apiBaseUrl?: string
  onMessage?: (msg: ExecutorMessage) => void
  onComplete?: (state: ExecutorState) => void
  onError?: (error: Error) => void
}

const DEFAULT_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

/**
 * Hook para executar agentes com streaming via SSE.
 *
 * @param options Configurações do executor
 * @returns Estado e funções de controle
 */
export function useAgentExecutor(options: UseAgentExecutorOptions = {}) {
  const {
    apiBaseUrl = DEFAULT_API_BASE_URL,
    onMessage,
    onComplete,
    onError,
  } = options

  const [state, setState] = useState<ExecutorState>({
    isLoading: false,
    isStreaming: false,
    response: '',
    error: null,
    toolCalls: [],
    sessionId: null,
    messages: [],
  })

  const eventSourceRef = useRef<EventSource | null>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  /**
   * Executa um agente com um prompt.
   *
   * @param agentSlug Slug do agente (ex: 'claims', 'agente-saneamento')
   * @param prompt Texto do prompt
   * @param options Opções adicionais (complexity, agent_code, agent_name, etc.)
   */
  const execute = useCallback(
    async (
      agentSlug: string,
      prompt: string,
      executorOptions?: {
        complexity?: 'simple' | 'normal' | 'complex'
        agentCode?: string
        agentName?: string
        userEmail?: string
        systemPromptOverride?: string
      },
    ) => {
      // Cancela execução anterior se ainda estiver rodando
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }

      setState((prev) => ({
        ...prev,
        isLoading: true,
        isStreaming: true,
        response: '',
        error: null,
        toolCalls: [],
        sessionId: null,
        messages: [],
      }))

      try {
        const url = `${apiBaseUrl}/executor/${agentSlug}`

        const requestBody = {
          prompt,
          complexity: executorOptions?.complexity || 'normal',
          agent_code: executorOptions?.agentCode || 'Manta XX',
          agent_name: executorOptions?.agentName || agentSlug,
          user_email: executorOptions?.userEmail || null,
          system_prompt_override: executorOptions?.systemPromptOverride || null,
        }

        // Usa fetch com response streaming para melhor controle
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        })

        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`HTTP ${response.status}: ${errorText}`)
        }

        if (!response.body) {
          throw new Error('Response body não disponível')
        }

        // Processa SSE manualmente via ReadableStream
        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''
        let currentSessionId: string | null = null
        let currentResponse = ''
        let currentToolCalls: Array<{ toolName: string; toolUseId: string }> = []
        let messageLog: ExecutorMessage[] = []

        while (true) {
          const { done, value } = await reader.read()

          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')

          // Mantém a última linha incompleta no buffer
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (!line.trim()) continue

            if (line.startsWith('event: ')) {
              const eventType = line.slice(7).trim()
              const dataIndex = lines.indexOf(
                lines.find((l) => l.startsWith('data: ')) || '',
              )

              if (dataIndex !== -1) {
                const dataLine = lines[dataIndex]
                const jsonStr = dataLine.slice(6).trim()

                try {
                  const data = JSON.parse(jsonStr)
                  const message: ExecutorMessage = {
                    type: eventType as ExecutorMessage['type'],
                    data,
                  }

                  messageLog.push(message)
                  onMessage?.(message)

                  // Atualiza estado baseado no tipo de evento
                  if (eventType === 'meta') {
                    currentSessionId = data.session_id
                  } else if (eventType === 'chunk') {
                    currentResponse += data.delta || ''
                  } else if (eventType === 'tool_use') {
                    currentToolCalls.push({
                      toolName: data.tool_name,
                      toolUseId: data.tool_use_id,
                    })
                  } else if (eventType === 'error') {
                    setState((prev) => ({
                      ...prev,
                      error: data.message || 'Erro desconhecido',
                    }))
                  } else if (eventType === 'done') {
                    setState((prev) => ({
                      ...prev,
                      isStreaming: false,
                      isLoading: false,
                      response: currentResponse,
                      sessionId: currentSessionId,
                      toolCalls: currentToolCalls,
                      messages: messageLog,
                    }))
                    onComplete?.({
                      isLoading: false,
                      isStreaming: false,
                      response: currentResponse,
                      error: null,
                      toolCalls: currentToolCalls,
                      sessionId: currentSessionId,
                      messages: messageLog,
                    })
                  }

                  // Atualiza estado incremental durante streaming
                  if (eventType === 'chunk' || eventType === 'meta') {
                    setState((prev) => ({
                      ...prev,
                      response: currentResponse,
                      sessionId: currentSessionId,
                      messages: messageLog,
                    }))
                  }
                } catch (e) {
                  console.error('Erro ao parsear evento SSE:', e, jsonStr)
                }
              }
            }
          }
        }

        // Processa buffer final
        if (buffer.trim()) {
          try {
            if (buffer.startsWith('data: ')) {
              const jsonStr = buffer.slice(6).trim()
              const data = JSON.parse(jsonStr)
              // Processa último evento se necessário
            }
          } catch (e) {
            console.error('Erro ao parsear último evento:', e)
          }
        }
      } catch (error) {
        const err = error instanceof Error ? error : new Error(String(error))
        setState((prev) => ({
          ...prev,
          isLoading: false,
          isStreaming: false,
          error: err.message,
        }))
        onError?.(err)
      }
    },
    [apiBaseUrl, onMessage, onComplete, onError],
  )

  /**
   * Cancela execução atual.
   */
  const cancel = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    setState((prev) => ({
      ...prev,
      isLoading: false,
      isStreaming: false,
    }))
  }, [])

  /**
   * Limpa estado.
   */
  const reset = useCallback(() => {
    cancel()
    setState({
      isLoading: false,
      isStreaming: false,
      response: '',
      error: null,
      toolCalls: [],
      sessionId: null,
      messages: [],
    })
  }, [cancel])

  /**
   * Limpa conexão ao desmontar hook.
   */
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [])

  return {
    state,
    execute,
    cancel,
    reset,
    isLoading: state.isLoading,
    isStreaming: state.isStreaming,
    response: state.response,
    error: state.error,
  }
}
