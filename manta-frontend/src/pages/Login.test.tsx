import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { Login } from '@/pages/Login'
import { useAuthStore } from '@/store/useAuthStore'
import type { MeResponse, TokenResponse } from '@/types/auth'

vi.mock('@/api/auth', () => ({
  login: vi.fn(),
  fetchMe: vi.fn(),
}))

import { fetchMe, login } from '@/api/auth'

const mockedLogin = vi.mocked(login)
const mockedFetchMe = vi.mocked(fetchMe)

const tokens: TokenResponse = {
  access_token: 'access-1',
  refresh_token: 'refresh-1',
  token_type: 'bearer',
  expires_in: 900,
  org_id: 'org-1',
  roles: ['owner'],
}

const me: MeResponse = {
  id: 'user-1',
  email: 'ana@example.com',
  full_name: 'Ana',
  is_active: true,
  is_superuser: false,
  active_org: {
    org_id: 'org-1',
    slug: 'ana-org',
    name: 'Ana Org',
    roles: ['owner'],
  },
  organizations: [],
}

function makeAxiosError(status: number, detail: unknown) {
  return Object.assign(new Error('Request failed'), {
    isAxiosError: true,
    response: { status, data: { detail } },
  })
}

function renderLogin(initialEntry = '/login') {
  return render(
    <MemoryRouter initialEntries={[initialEntry]}>
      <Routes>
        <Route path="/" element={<div>Home page</div>} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </MemoryRouter>,
  )
}

describe('Login', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    })
    localStorage.clear()
    mockedLogin.mockReset()
    mockedFetchMe.mockReset()
  })

  it('renders email and password fields', () => {
    renderLogin()

    expect(screen.getByLabelText('E-mail')).toBeInTheDocument()
    expect(screen.getByLabelText('Senha')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeInTheDocument()
  })

  it('redirects immediately if already authenticated', () => {
    useAuthStore.getState().setAuth({ accessToken: 'a', refreshToken: 'r' })

    renderLogin()

    expect(screen.getByText('Home page')).toBeInTheDocument()
  })

  it('logs in, stores tokens/user, and redirects to /', async () => {
    const user = userEvent.setup()
    mockedLogin.mockResolvedValue(tokens)
    mockedFetchMe.mockResolvedValue(me)

    renderLogin()

    await user.type(screen.getByLabelText('E-mail'), 'ana@example.com')
    await user.type(screen.getByLabelText('Senha'), 'senha-super-secreta')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    await waitFor(() => {
      expect(screen.getByText('Home page')).toBeInTheDocument()
    })

    expect(mockedLogin).toHaveBeenCalledWith({
      email: 'ana@example.com',
      password: 'senha-super-secreta',
      org_id: undefined,
    })
    expect(useAuthStore.getState().accessToken).toBe('access-1')
    expect(useAuthStore.getState().user).toEqual(me)
  })

  it('shows an error message on invalid credentials', async () => {
    const user = userEvent.setup()
    mockedLogin.mockRejectedValue(makeAxiosError(401, 'Credenciais inválidas.'))

    renderLogin()

    await user.type(screen.getByLabelText('E-mail'), 'ana@example.com')
    await user.type(screen.getByLabelText('Senha'), 'senha-errada')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'Credenciais inválidas.',
    )
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
  })

  it('shows an organization picker when the user belongs to multiple orgs', async () => {
    const user = userEvent.setup()
    mockedLogin.mockRejectedValueOnce(
      makeAxiosError(400, {
        message: 'Usuário pertence a múltiplas organizações — informe org_id.',
        organizations: [
          { org_id: 'org-1', slug: 'org-1', name: 'Org Um', roles: ['owner'] },
          {
            org_id: 'org-2',
            slug: 'org-2',
            name: 'Org Dois',
            roles: ['member'],
          },
        ],
      }),
    )
    mockedLogin.mockResolvedValueOnce(tokens)
    mockedFetchMe.mockResolvedValue(me)

    renderLogin()

    await user.type(screen.getByLabelText('E-mail'), 'ana@example.com')
    await user.type(screen.getByLabelText('Senha'), 'senha-super-secreta')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    expect(await screen.findByLabelText('Organização')).toBeInTheDocument()
    expect(screen.getByText('Org Um')).toBeInTheDocument()
    expect(screen.getByText('Org Dois')).toBeInTheDocument()

    await user.selectOptions(screen.getByLabelText('Organização'), 'org-2')
    await user.click(screen.getByRole('button', { name: 'Entrar' }))

    await waitFor(() => {
      expect(mockedLogin).toHaveBeenLastCalledWith({
        email: 'ana@example.com',
        password: 'senha-super-secreta',
        org_id: 'org-2',
      })
    })
  })
})
