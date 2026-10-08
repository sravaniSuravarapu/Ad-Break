import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { AuthLayout, AuthLink } from '../components/AuthLayout'
import { Alert, Button, Field, controlClass } from '../components/ui'
import { useAuth } from '../hooks/useAuth'

const schema = z.object({
  email: z.string().min(3),
  password: z.string().min(8),
})

type FormValues = z.infer<typeof schema>

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const form = useForm<FormValues>({ resolver: zodResolver(schema) })

  return (
    <AuthLayout title="Sign in" subtitle="Use a demo account or your own." footer={<span>New here? <AuthLink to="/signup">Create an account</AuthLink></span>}>
      <form
        className="space-y-4"
        onSubmit={form.handleSubmit(async (values) => {
          setError(null)
          try {
            await login(values.email, values.password)
            navigate('/')
          } catch (err) {
            setError(err instanceof Error ? err.message : 'Sign in failed.')
          }
        })}
      >
        {error && <Alert>{error}</Alert>}
        <Field label="Email">
          <input className={controlClass} type="email" {...form.register('email')} />
        </Field>
        <Field label="Password">
          <input className={controlClass} type="password" {...form.register('password')} />
        </Field>
        <Button className="w-full" type="submit" disabled={form.formState.isSubmitting}>
          Sign in
        </Button>
        <p className="text-xs text-[var(--muted)]">Demo password Demo@12345 for sales@example.com, traffic@example.com, and revenue@example.com.</p>
      </form>
    </AuthLayout>
  )
}
