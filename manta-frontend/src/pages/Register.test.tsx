import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { Register } from '@/pages/Register'
import { useAuthStore } from '@/store/useAuthStore'
import type { MeResponse, RegisterResponse, TokenResponse } from '@/types/auth'

vi.mock('@/api/auth', () => ({
  login: vi.fn(),
  register: vi.fn(),
  fetchMe: vi.fn(),
}))

import { fetchMe, login, register } from '@/api/auth'

const mockedLogin = vi.mocked(login)
const mockedRegister = vi.mocked(register)
const mockedFetchMe = vi.mocked(fetchMe)

const registerResponse: RegisterResponse = {
  user: {
    id: 'user-1',
    email: 'ana@example.com',
    full_name: 'Ana',
    is_active: true,
    is_superuser: false,
  },
  organization: {
    org_id: 'org-1',
    slug: 'ana-org',
    name: 'Ana Org',
    roles: ['owner'],
  },
}

const tokens: TokenResponse = {
  access_token: 'access-1',
  refresh_token: 'refresh-1',
  token_type: 'bearer',
  expires_in: 900,
  org_id: 'org-1',
  roles: ['owner'],
}

const me: MeResponse = {
  ...registerResponse.user,
  active_org: registerResponse.organization,
  organizations: [registerResponse.organization],
}

function makeAxiosError(status: number, detail: unknown) {
  return Object.assign(new Error('Request failed'), {
    isAxiosError: true,
    response: { status, data: { detail } },
  })
}

function renderRegister() {
  return render(
    <MemoryRouter initialEntries={['/register']}>
      <Routes>
        <Route path="/" element={<div>Home page</div>} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </MemoryRouter>,
  )
}

async function fillAndSubmit(
  user: ReturnType<typeof userEvent.setup>,
  overrides: Partial<{
    fullName: string
    email: string
    password: string
    orgName: string
  }> = {},
) {
  const {
    fullName = 'Ana Souza',
    email = 'ana@example.com',
    password = 'senha-super-secreta',
    orgName = 'Ana Org',
  } = overrides

  if (fullName)
    await user.type(screen.getByLabelText('Nome completo'), fullName)
  await user.type(screen.getByLabelText('E-mail'), email)
  await user.type(screen.getByLabelText('Senha'), password)
  if (orgName) await user.type(screen.getByLabelText('Organização'), orgName)
  await user.click(screen.getByRole('button', { name: 'Criar conta' }))
}

describe('Register', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    })
    localStorage.clear()
    mockedLogin.mockReset()
    mockedRegister.mockReset()
    mockedFetchMe.mockReset()
  })

  it('renders all required fields', () => {
    renderRegister()

    expect(screen.getByLabelText('Nome completo')).toBeInTheDocument()
    expect(screen.getByLabelText('E-mail')).toBeInTheDocument()
    expect(screen.getByLabelText('Senha')).toBeInTheDocument()
    expect(screen.getByLabelText('Organização')).toBeInTheDocument()
  })

  it('redirects immediately if already authenticated', () => {
    useAuthStore.getState().setAuth({ accessToken: 'a', refreshToken: 'r' })

    renderRegister()

    expect(screen.getByText('Home page')).toBeInTheDocument()
  })

  it('rejects passwords shorter than 8 characters without calling the API', async () => {
    const user = userEvent.setup()
    renderRegister()

    await fillAndSubmit(user, { password: 'short' })

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'pelo menos 8 caracteres',
    )
    expect(mockedRegister).not.toHaveBeenCalled()
  })

  it('registers, auto-logs in, stores the session and redirects to /', async () => {
    const user = userEvent.setup()
    mockedRegister.mockResolvedValue(registerResponse)
    mockedLogin.mockResolvedValue(tokens)
    mockedFetchMe.mockResolvedValue(me)

    renderRegister()

    await fillAndSubmit(user)

    await waitFor(() => {
      expect(screen.getByText('Home page')).toBeInTheDocument()
    })

    expect(mockedRegister).toHaveBeenCalledWith({
      email: 'ana@example.com',
      password: 'senha-super-secreta',
      full_name: 'Ana Souza',
      org_name: 'Ana Org',
    })
    expect(mockedLogin).toHaveBeenCalledWith({
      email: 'ana@example.com',
      password: 'senha-super-secreta',
    })
    expect(useAuthStore.getState().accessToken).toBe('access-1')
    expect(useAuthStore.getState().user).toEqual(me)
  })

  it('shows an error when the email is already registered', async () => {
    const user = userEvent.setup()
    mockedRegister.mockRejectedValue(
      makeAxiosError(409, 'E-mail já cadastrado.'),
    )

    renderRegister()

    await fillAndSubmit(user)

    expect(await screen.findByRole('alert')).toHaveTextContent(
      'E-mail já cadastrado.',
    )
    expect(mockedLogin).not.toHaveBeenCalled()
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
  })
})
