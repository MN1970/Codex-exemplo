import { useEffect, useState, type FormEvent } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { fetchMe, login } from '@/api/auth'
import { useAuthStore } from '@/store/useAuthStore'
import { getErrorMessage, getMultiOrgErrorDetail } from '@/lib/errors'
import type { OrgMembership } from '@/types/auth'

interface LocationState {
  from?: { pathname: string }
}

/**
 * Sign-in form: POST /auth/login → store tokens → GET /auth/me to
 * populate the profile → redirect to wherever `ProtectedRoute` sent the
 * user from (or `/` for a direct visit to `/login`).
 *
 * Handles the backend's multi-organization case: if a user belongs to
 * more than one org, `/auth/login` responds 400 with the list of orgs and
 * asks for `org_id` — this form then renders a picker and resubmits.
 */
export function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const setAuth = useAuthStore((s) => s.setAuth)
  const setUser = useAuthStore((s) => s.setUser)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [organizations, setOrganizations] = useState<OrgMembership[] | null>(
    null,
  )
  const [orgId, setOrgId] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    document.title = 'Manta Frontend — Entrar'
  }, [])

  if (isAuthenticated) {
    const redirectTo =
      (location.state as LocationState | null)?.from?.pathname ?? '/'
    return <Navigate to={redirectTo} replace />
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const tokens = await login({
        email,
        password,
        org_id: orgId || undefined,
      })
      setAuth({
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
      })

      try {
        const me = await fetchMe()
        setUser(me)
      } catch {
        // Non-fatal: tokens are valid either way, /me just fills in the
        // profile. Leaving `user` null here still keeps the user signed in.
      }

      const redirectTo =
        (location.state as LocationState | null)?.from?.pathname ?? '/'
      navigate(redirectTo, { replace: true })
    } catch (err) {
      const multiOrg = getMultiOrgErrorDetail(err)
      if (multiOrg) {
        setOrganizations(multiOrg.organizations)
        setError(multiOrg.message)
      } else {
        setError(getErrorMessage(err, 'E-mail ou senha inválidos.'))
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="mx-auto flex max-w-sm flex-col gap-6 py-12">
      <Card>
        <CardHeader>
          <CardTitle>Entrar</CardTitle>
          <CardDescription>
            Acesse sua conta Manta com e-mail e senha.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form
            className="flex flex-col gap-4"
            onSubmit={handleSubmit}
            noValidate
          >
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="email">E-mail</Label>
              <Input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="password">Senha</Label>
              <Input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            {organizations && organizations.length > 0 && (
              <div className="flex flex-col gap-1.5">
                <Label htmlFor="org">Organização</Label>
                <select
                  id="org"
                  name="org"
                  required
                  value={orgId}
                  onChange={(e) => setOrgId(e.target.value)}
                  disabled={isSubmitting}
                  className="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  <option value="" disabled>
                    Selecione uma organização
                  </option>
                  {organizations.map((org) => (
                    <option key={org.org_id} value={org.org_id}>
                      {org.name}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {error && (
              <p role="alert" className="text-sm text-destructive">
                {error}
              </p>
            )}

            <Button type="submit" disabled={isSubmitting} className="mt-2">
              {isSubmitting ? 'Entrando…' : 'Entrar'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <p className="text-center text-sm text-muted-foreground">
        Não tem conta?{' '}
        <Link to="/register" className="text-primary hover:underline">
          Cadastre-se
        </Link>
      </p>
    </div>
  )
}
