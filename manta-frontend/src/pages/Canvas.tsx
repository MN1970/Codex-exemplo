import { useEffect, useMemo, useState } from 'react'
import { Bot, PanelLeftClose, PanelLeftOpen, RefreshCw, Search } from 'lucide-react'
import { AgentCard } from '@/components/canvas/AgentCard'
import { LoadingSpinner } from '@/components/canvas/LoadingSpinner'
import { PromptForm } from '@/components/canvas/PromptForm'
import { ResponseViewer } from '@/components/canvas/ResponseViewer'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { getAgents } from '@/api/agents'
import { useAgentInvoke } from '@/hooks/useAgentInvoke'
import { getErrorMessage } from '@/lib/errors'
import { cn } from '@/lib/utils'
import { useAppStore } from '@/store/useAppStore'
import type { Agent } from '@/types/agents'

/**
 * Canvas — pick an agent from the searchable sidebar, send it a prompt,
 * and watch the reply stream in via SSE (`POST /agents/{slug}/invoke`).
 * The backend persists the full prompt/response pair once the stream
 * completes (`agent_sessions` table, `GET /agents/{slug}/sessions`).
 */
export function Canvas() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [agentsLoading, setAgentsLoading] = useState(true)
  const [agentsError, setAgentsError] = useState<string | null>(null)
  const [reloadTick, setReloadTick] = useState(0)
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<Agent | null>(null)

  const sidebarOpen = useAppStore((s) => s.sidebarOpen)
  const toggleSidebar = useAppStore((s) => s.toggleSidebar)

  const { status, content, error, invoke, cancel, reset } = useAgentInvoke()

  useEffect(() => {
    document.title = 'Manta Frontend — Canvas'
  }, [])

  useEffect(() => {
    let active = true

    getAgents()
      .then((data) => {
        if (!active) return
        setAgents(data)
        setSelected((prev) => prev ?? data[0] ?? null)
      })
      .catch((err) => {
        if (!active) return
        setAgentsError(getErrorMessage(err, 'Não foi possível carregar os agentes.'))
      })
      .finally(() => {
        if (active) setAgentsLoading(false)
      })

    return () => {
      active = false
    }
  }, [reloadTick])

  const filteredAgents = useMemo(() => {
    const query = search.trim().toLowerCase()
    if (!query) return agents
    return agents.filter((agent) =>
      [agent.name, agent.code, agent.slug, ...agent.aliases].some((field) =>
        field.toLowerCase().includes(query),
      ),
    )
  }, [agents, search])

  function handleSelectAgent(agent: Agent) {
    if (agent.code === selected?.code) return
    setSelected(agent)
    reset()
  }

  function handleSubmit(prompt: string) {
    if (!selected) return
    void invoke(selected.slug, prompt)
  }

  return (
    <div className="flex h-full flex-col">
      {/* Canvas header */}
      <div className="flex items-center justify-between gap-3 border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            aria-label={sidebarOpen ? 'Fechar lista de agentes' : 'Abrir lista de agentes'}
            className="md:hidden"
          >
            {sidebarOpen ? (
              <PanelLeftClose className="h-4 w-4" />
            ) : (
              <PanelLeftOpen className="h-4 w-4" />
            )}
          </Button>
          <Bot className="h-5 w-5 text-primary" aria-hidden="true" />
          <div>
            <h1 className="text-base font-semibold leading-none">Canvas de Agentes</h1>
            <p className="mt-1 text-xs text-muted-foreground">
              {agentsLoading
                ? 'Carregando…'
                : `${agents.length} agente${agents.length === 1 ? '' : 's'} disponíve${agents.length === 1 ? 'l' : 'is'}`}
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside
          className={cn(
            'w-72 shrink-0 flex-col overflow-hidden border-r border-border',
            sidebarOpen ? 'flex' : 'hidden md:flex',
          )}
        >
          <div className="border-b border-border p-3">
            <div className="relative">
              <Search
                className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
                aria-hidden="true"
              />
              <Input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Buscar agente…"
                aria-label="Buscar agente"
                className="pl-8"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-2">
            {agentsLoading && (
              <div className="p-4">
                <LoadingSpinner label="Carregando agentes…" />
              </div>
            )}

            {!agentsLoading && agentsError && (
              <div className="flex flex-col gap-2 p-3">
                <p className="text-sm text-destructive">{agentsError}</p>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setAgentsLoading(true)
                    setAgentsError(null)
                    setReloadTick((t) => t + 1)
                  }}
                >
                  <RefreshCw className="h-4 w-4" />
                  Tentar de novo
                </Button>
              </div>
            )}

            {!agentsLoading && !agentsError && filteredAgents.length === 0 && (
              <p className="p-3 text-sm text-muted-foreground">
                Nenhum agente encontrado para &quot;{search}&quot;.
              </p>
            )}

            {!agentsLoading && !agentsError && filteredAgents.length > 0 && (
              <div className="flex flex-col gap-1">
                {filteredAgents.map((agent) => (
                  <AgentCard
                    key={agent.code}
                    agent={agent}
                    selected={selected?.code === agent.code}
                    onSelect={handleSelectAgent}
                  />
                ))}
              </div>
            )}
          </div>
        </aside>

        {/* Main canvas */}
        <main className="flex flex-1 flex-col gap-4 overflow-y-auto p-4">
          {selected ? (
            <>
              <div>
                <h2 className="text-lg font-semibold">{selected.name}</h2>
                <p className="text-sm text-muted-foreground">
                  {selected.code} · tier {selected.tier} · {selected.status}
                </p>
              </div>

              <ResponseViewer
                status={status}
                content={content}
                error={error}
                agentName={selected.name}
                className="flex-1"
              />

              <PromptForm
                disabled={status === 'streaming'}
                isStreaming={status === 'streaming'}
                onSubmit={handleSubmit}
                onCancel={cancel}
                placeholder={`Pergunte algo para ${selected.name}…`}
              />
            </>
          ) : (
            <p className="m-auto text-sm text-muted-foreground">
              {agentsLoading
                ? 'Carregando agentes…'
                : agentsError
                  ? 'Não foi possível carregar os agentes.'
                  : 'Selecione um agente na barra lateral.'}
            </p>
          )}
        </main>
      </div>
    </div>
  )
}
