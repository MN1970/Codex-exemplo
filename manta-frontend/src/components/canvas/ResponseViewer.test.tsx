import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { ResponseViewer } from '@/components/canvas/ResponseViewer'

describe('ResponseViewer', () => {
  it('shows the empty-state prompt when idle with no content', () => {
    render(
      <ResponseViewer status="idle" content="" error={null} agentName="maestro" />,
    )
    expect(screen.getByText(/Envie um prompt para maestro/)).toBeInTheDocument()
  })

  it('shows a waiting spinner once streaming starts before the first token', () => {
    render(<ResponseViewer status="streaming" content="" error={null} />)
    expect(screen.getByRole('status')).toBeInTheDocument()
    expect(screen.getAllByText('Aguardando resposta…').length).toBeGreaterThan(0)
  })

  it('renders streamed content as it grows', () => {
    render(<ResponseViewer status="streaming" content="Olá mundo" error={null} />)
    expect(screen.getByText(/Olá mundo/)).toBeInTheDocument()
  })

  it('renders the error message when status is error', () => {
    render(
      <ResponseViewer status="error" content="" error="Falha ao invocar o agente." />,
    )
    expect(screen.getByText('Falha ao invocar o agente.')).toBeInTheDocument()
  })
})
