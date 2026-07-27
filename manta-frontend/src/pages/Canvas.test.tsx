import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Canvas } from '@/pages/Canvas'
import * as agentsApi from '@/api/agents'
import type { Agent } from '@/types/agents'

vi.mock('@/api/agents', async () => {
  const actual = await vi.importActual<typeof agentsApi>('@/api/agents')
  return {
    ...actual,
    getAgents: vi.fn(),
    invokeAgentStream: vi.fn(),
  }
})

const mockedGetAgents = vi.mocked(agentsApi.getAgents)
const mockedInvokeStream = vi.mocked(agentsApi.invokeAgentStream)

const agents: Agent[] = [
  {
    code: 'Manta 00',
    slug: 'maestro',
    name: 'maestro',
    aliases: ['manta-router'],
    tier: 'Haiku→Sonnet',
    status: 'operacional',
    axis: 'horizontal',
  },
  {
    code: 'Manta 03-S8',
    slug: 'agente-saneamento',
    name: 'agente-saneamento',
    aliases: [],
    tier: 'Sonnet',
    status: 'operacional',
    axis: 'vertical',
  },
]

afterEach(() => {
  mockedGetAgents.mockReset()
  mockedInvokeStream.mockReset()
})

function renderCanvas() {
  return render(
    <MemoryRouter>
      <Canvas />
    </MemoryRouter>,
  )
}

describe('Canvas', () => {
  it('loads and lists agents, auto-selecting the first one', async () => {
    mockedGetAgents.mockResolvedValue(agents)
    renderCanvas()

    const sidebar = screen.getByRole('complementary')
    expect(await within(sidebar).findByText('maestro')).toBeInTheDocument()
    expect(within(sidebar).getByText('agente-saneamento')).toBeInTheDocument()
    expect(screen.getByText('2 agentes disponíveis')).toBeInTheDocument()

    // Auto-selected first agent shows up as the main-panel heading.
    const main = screen.getByRole('main')
    expect(within(main).getByRole('heading', { name: 'maestro' })).toBeInTheDocument()
  })

  it('filters the sidebar list via the search box', async () => {
    mockedGetAgents.mockResolvedValue(agents)
    const user = userEvent.setup()
    renderCanvas()

    const sidebar = screen.getByRole('complementary')
    await within(sidebar).findByText('maestro')

    await user.type(screen.getByPlaceholderText('Buscar agente…'), 'saneamento')

    expect(within(sidebar).queryByText('maestro')).not.toBeInTheDocument()
    expect(within(sidebar).getByText('agente-saneamento')).toBeInTheDocument()
  })

  it('submitting a prompt invokes the selected agent and streams the reply', async () => {
    mockedGetAgents.mockResolvedValue(agents)
    mockedInvokeStream.mockImplementation(async (_slug, _prompt, handlers) => {
      handlers.onMeta?.({ session_id: 's-1', agent_slug: 'maestro', agent_code: 'Manta 00' })
      handlers.onChunk?.('oi ')
      handlers.onChunk?.('humano')
      handlers.onDone?.({ session_id: 's-1', full_response: 'oi humano' })
    })

    const user = userEvent.setup()
    renderCanvas()

    const sidebar = screen.getByRole('complementary')
    await within(sidebar).findByText('maestro')

    await user.type(
      screen.getByLabelText('Prompt para o agente'),
      'diga oi{Enter}',
    )

    expect(mockedInvokeStream).toHaveBeenCalledWith(
      'maestro',
      'diga oi',
      expect.anything(),
      expect.anything(),
    )

    await waitFor(() => expect(screen.getByText(/oi humano/)).toBeInTheDocument())
  })

  it('shows an error and a retry button when loading agents fails', async () => {
    mockedGetAgents.mockRejectedValue(new Error('network down'))
    renderCanvas()

    expect(await screen.findByText('network down')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Tentar de novo/ })).toBeInTheDocument()
  })
})
