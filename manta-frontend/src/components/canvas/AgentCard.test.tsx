import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { AgentCard } from '@/components/canvas/AgentCard'
import type { Agent } from '@/types/agents'

const agent: Agent = {
  code: 'Manta 03-S8',
  slug: 'agente-saneamento',
  name: 'agente-saneamento',
  aliases: [],
  tier: 'Sonnet',
  status: 'operacional',
  axis: 'vertical',
}

describe('AgentCard', () => {
  it('renders name, code and tier', () => {
    render(<AgentCard agent={agent} />)
    expect(screen.getByText('agente-saneamento')).toBeInTheDocument()
    expect(screen.getByText('Manta 03-S8')).toBeInTheDocument()
    expect(screen.getByText('Sonnet')).toBeInTheDocument()
  })

  it('marks itself pressed when selected', () => {
    render(<AgentCard agent={agent} selected />)
    expect(screen.getByRole('button')).toHaveAttribute('aria-pressed', 'true')
  })

  it('calls onSelect with the agent when clicked', async () => {
    const onSelect = vi.fn()
    const user = userEvent.setup()
    render(<AgentCard agent={agent} onSelect={onSelect} />)

    await user.click(screen.getByRole('button'))

    expect(onSelect).toHaveBeenCalledWith(agent)
  })
})
