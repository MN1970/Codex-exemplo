/**
 * components/AgentExecutor.tsx — Interface de execução de agentes.
 *
 * Exibe seletor de agente, input de prompt, resultado streamado com
 * ferramentas MCP e tratamento de erros.
 */
import { AlertCircle, Loader2, Send, Zap } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAgentExecutor, ExecutorMessage } from '@/hooks/useAgentExecutor'

interface AgentOption {
  slug: string
  name: string
  code: string
  tier: string
}

interface AgentExecutorProps {
  agents?: AgentOption[]
  onSessionCreated?: (sessionId: string) => void
}

const DEFAULT_AGENTS: AgentOption[] = [
  {
    slug: 'maestro',
    name: 'Maestro (Router)',
    code: 'Manta 00',
    tier: 'Haiku→Sonnet',
  },
  {
    slug: 'claims',
    name: 'Claims',
    code: 'Manta 01',
    tier: 'Opus',
  },
  {
    slug: 'contratual',
    name: 'Contratual',
    code: 'Manta 02',
    tier: 'Sonnet',
  },
  {
    slug: 'orcamento',
    name: 'Orçamento',
    code: 'Manta 05',
    tier: 'Sonnet',
  },
  {
    slug: 'agente-saneamento',
    name: 'Saneamento (S8)',
    code: 'Manta 03-S8',
    tier: 'Sonnet',
  },
  {
    slug: 'agente-energia',
    name: 'Energia (S9)',
    code: 'Manta 03-S9',
    tier: 'Sonnet',
  },
]

/**
 * Componente de execução de agentes com streaming SSE.
 */
export function AgentExecutor({ agents = DEFAULT_AGENTS, onSessionCreated }: AgentExecutorProps) {
  const [selectedAgent, setSelectedAgent] = useState<AgentOption>(agents[0])
  const [prompt, setPrompt] = useState('')
  const [complexity, setComplexity] = useState<'simple' | 'normal' | 'complex'>('normal')
  const [messages, setMessages] = useState<Array<{ type: 'user' | 'assistant' | 'tool'; content: string }>>([])
  const [toolEvents, setToolEvents] = useState<Array<{ type: string; toolName?: string; error?: string }>>([])

  const messageEndRef = useRef<HTMLDivElement>(null)
  const { execute, cancel, reset, state, isLoading, isStreaming, response, error } = useAgentExecutor({
    onMessage: handleStreamMessage,
    onComplete: handleComplete,
  })

  // Auto-scroll para o fim das mensagens
  useEffect(() => {
    messageEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, response])

  /**
   * Callback para novos eventos SSE.
   */
  function handleStreamMessage(msg: ExecutorMessage) {
    if (msg.type === 'meta') {
      onSessionCreated?.(msg.data.session_id)
    } else if (msg.type === 'chunk') {
      // Atualizado incrementalmente via state do hook
    } else if (msg.type === 'tool_use') {
      setToolEvents((prev) => [
        ...prev,
        {
          type: 'tool_use',
          toolName: msg.data.tool_name,
        },
      ])
    } else if (msg.type === 'tool_error') {
      setToolEvents((prev) => [
        ...prev,
        {
          type: 'tool_error',
          toolName: msg.data.tool_name,
          error: msg.data.error,
        },
      ])
    }
  }

  /**
   * Callback quando execução completa.
   */
  function handleComplete() {
    if (response) {
      setMessages((prev) => [
        ...prev,
        {
          type: 'assistant',
          content: response,
        },
      ])
    }
  }

  /**
   * Submete o prompt para execução.
   */
  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()

      if (!prompt.trim()) return

      // Adiciona prompt do usuário ao histórico
      setMessages((prev) => [
        ...prev,
        {
          type: 'user',
          content: prompt,
        },
      ])

      // Reseta para nova execução
      setToolEvents([])

      // Executa agente
      await execute(selectedAgent.slug, prompt, {
        complexity,
        agentCode: selectedAgent.code,
        agentName: selectedAgent.name,
      })

      // Limpa prompt
      setPrompt('')
    },
    [execute, selectedAgent, complexity, prompt],
  )

  /**
   * Handler para mudança de agente.
   */
  const handleAgentChange = useCallback((slug: string) => {
    const agent = agents.find((a) => a.slug === slug)
    if (agent) {
      setSelectedAgent(agent)
    }
  }, [agents])

  /**
   * Handler para limpar conversa.
   */
  const handleClear = useCallback(() => {
    reset()
    setMessages([])
    setToolEvents([])
    setPrompt('')
  }, [reset])

  return (
    <div className="grid gap-4 h-full">
      {/* Seletor de Agente e Configurações */}
      <Card className="p-4">
        <div className="grid gap-4">
          {/* Seletor de Agente */}
          <div className="grid gap-2">
            <Label htmlFor="agent-select">Agente</Label>
            <select
              id="agent-select"
              value={selectedAgent.slug}
              onChange={(e) => handleAgentChange(e.target.value)}
              disabled={isLoading}
              className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {agents.map((agent) => (
                <option key={agent.slug} value={agent.slug}>
                  {agent.name} ({agent.code}) - {agent.tier}
                </option>
              ))}
            </select>
          </div>

          {/* Seletor de Complexidade */}
          <div className="grid gap-2">
            <Label htmlFor="complexity-select">Complexidade</Label>
            <select
              id="complexity-select"
              value={complexity}
              onChange={(e) => setComplexity(e.target.value as 'simple' | 'normal' | 'complex')}
              disabled={isLoading}
              className="flex h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <option value="simple">Simples (Sonnet)</option>
              <option value="normal">Normal (Sonnet)</option>
              <option value="complex">Complexa (Opus)</option>
            </select>
          </div>

          {/* Buttons */}
          <div className="flex gap-2">
            {isLoading && (
              <Button onClick={cancel} variant="destructive" size="sm">
                Cancelar
              </Button>
            )}
            {messages.length > 0 && !isLoading && (
              <Button onClick={handleClear} variant="outline" size="sm">
                Limpar
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* Histórico de Mensagens */}
      <Card className="flex-1 overflow-y-auto p-4">
        <div className="grid gap-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <p>Nenhuma conversa ainda. Digite um prompt abaixo para começar.</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`grid gap-1 ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`rounded-lg px-4 py-2 max-w-md lg:max-w-lg break-words ${
                    msg.type === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : msg.type === 'tool'
                        ? 'bg-muted text-muted-foreground text-sm italic'
                        : 'bg-secondary text-secondary-foreground'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))
          )}

          {/* Resposta em Streaming */}
          {isStreaming && response && (
            <div className="grid gap-1 justify-start">
              <div className="rounded-lg px-4 py-2 bg-secondary text-secondary-foreground break-words">
                {response}
                <span className="animate-pulse">▌</span>
              </div>
            </div>
          )}

          {/* Eventos de Ferramenta */}
          {toolEvents.length > 0 && (
            <div className="grid gap-2 bg-muted p-3 rounded-lg">
              <p className="text-xs font-semibold text-muted-foreground">Ferramentas Utilizadas:</p>
              {toolEvents.map((event, idx) => (
                <div key={idx} className="text-xs flex items-center gap-2">
                  {event.type === 'tool_use' ? (
                    <>
                      <Zap className="h-3 w-3" />
                      <span>{event.toolName}</span>
                    </>
                  ) : (
                    <>
                      <AlertCircle className="h-3 w-3 text-destructive" />
                      <span className="text-destructive">
                        {event.toolName}: {event.error}
                      </span>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Erro */}
          {error && !isStreaming && (
            <div className="grid gap-1 justify-start">
              <div className="rounded-lg px-4 py-2 bg-destructive/10 border border-destructive/20 text-destructive text-sm flex items-start gap-2">
                <AlertCircle className="h-4 w-4 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </div>
            </div>
          )}

          <div ref={messageEndRef} />
        </div>
      </Card>

      {/* Input de Prompt */}
      <Card className="p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            placeholder="Digite seu prompt aqui..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoading}
            className="flex-1"
            autoFocus
          />
          <Button
            type="submit"
            disabled={isLoading || !prompt.trim()}
            size="icon"
            className="flex-shrink-0"
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </Button>
        </form>
      </Card>
    </div>
  )
}
