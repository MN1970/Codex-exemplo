import { useEffect, useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
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
import { fetchMe, login, register } from '@/api/auth'
import { useAuthStore } from '@/store/useAuthStore'
import { getErrorMessage } from '@/lib/errors'

const MIN_PASSWORD_LENGTH = 8

/**
 * Sign-up form: POST /auth/register (creates the user + a brand-new
 * organization, which the backend makes the user "owner" of), then
 * immediately POST /auth/login with the same credentials to obtain
 * tokens — `/auth/register` itself only returns the created user/org,
 * not a session — and redirect to `/`.
 */
export function Register() {
  const navigate = useNavigate()
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const setAuth = useAuthStore((s) => s.setAuth)
  const setUser = useAuthStore((s) => s.setUser)

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [orgName, setOrgName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    document.title = 'Manta Frontend — Criar conta'
  }, [])

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    if (password.length < MIN_PASSWORD_LENGTH) {
      setError(
        `A senha precisa ter pelo menos ${MIN_PASSWORD_LENGTH} caracteres.`,
      )
      return
    }

    setIsSubmitting(true)
    try {
      await register({
        email,
        password,
        full_name: fullName,
        org_name: orgName,
      })

      const tokens = await login({ email, password })
      setAuth({
        accessToken: tokens.access_token,
        refreshToken: tokens.refresh_token,
      })

      try {
        const me = await fetchMe()
        setUser(me)
      } catch {
        // Non-fatal — see Login.tsx for the same tradeoff.
      }

      navigate('/', { replace: true })
    } catch (err) {
      setError(getErrorMessage(err, 'Não foi possível criar a conta.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="mx-auto flex max-w-sm flex-col gap-6 py-12">
      <Card>
        <CardHeader>
          <CardTitle>Criar conta</CardTitle>
          <CardDescription>
            Cria seu usuário e uma organização nova (você vira o administrador
            dela).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form
            className="flex flex-col gap-4"
            onSubmit={handleSubmit}
            noValidate
          >
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="full_name">Nome completo</Label>
              <Input
                id="full_name"
                name="full_name"
                type="text"
                autoComplete="name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

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
                autoComplete="new-password"
                required
                minLength={MIN_PASSWORD_LENGTH}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <Label htmlFor="org_name">Organização</Label>
              <Input
                id="org_name"
                name="org_name"
                type="text"
                required
                minLength={2}
                placeholder="Nome da sua empresa/organização"
                value={orgName}
                onChange={(e) => setOrgName(e.target.value)}
                disabled={isSubmitting}
              />
            </div>

            {error && (
              <p role="alert" className="text-sm text-destructive">
                {error}
              </p>
            )}

            <Button type="submit" disabled={isSubmitting} className="mt-2">
              {isSubmitting ? 'Criando conta…' : 'Criar conta'}
            </Button>
          </form>
        </CardContent>
      </Card>

      <p className="text-center text-sm text-muted-foreground">
        Já tem conta?{' '}
        <Link to="/login" className="text-primary hover:underline">
          Entrar
        </Link>
      </p>
    </div>
  )
}
