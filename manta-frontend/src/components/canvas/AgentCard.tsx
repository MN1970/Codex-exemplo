import { cn } from '@/lib/utils'
import type { Agent } from '@/types/agents'

const STATUS_DOT: Record<Agent['status'], string> = {
  operacional: 'bg-emerald-500',
  parcial: 'bg-amber-500',
  planejado: 'bg-muted-foreground/40',
}

const STATUS_LABEL: Record<Agent['status'], string> = {
  operacional: 'Operacional',
  parcial: 'Parcial',
  planejado: 'Planejado',
}

export interface AgentCardProps {
  agent: Agent
  selected?: boolean
  onSelect?: (agent: Agent) => void
}

/** One row in the Canvas sidebar's agent list — selectable, shows status/tier. */
export function AgentCard({ agent, selected = false, onSelect }: AgentCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(agent)}
      aria-pressed={selected}
      title={agent.aliases.length ? `Aliases: ${agent.aliases.join(', ')}` : undefined}
      className={cn(
        'w-full rounded-md border px-3 py-2.5 text-left transition-colors',
        'hover:bg-accent hover:text-accent-foreground',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
        selected
          ? 'border-primary/40 bg-primary/10'
          : 'border-transparent bg-transparent',
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="truncate text-sm font-medium">{agent.name}</span>
        <span
          className={cn('h-2 w-2 shrink-0 rounded-full', STATUS_DOT[agent.status])}
          aria-label={STATUS_LABEL[agent.status]}
        />
      </div>
      <div className="mt-0.5 flex items-center justify-between gap-2 text-xs text-muted-foreground">
        <span className="truncate">{agent.code}</span>
        <span className="shrink-0 rounded bg-muted px-1.5 py-0.5 font-mono">
          {agent.tier}
        </span>
      </div>
    </button>
  )
}
