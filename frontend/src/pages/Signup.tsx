import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { AuthLayout, AuthLink } from '../components/AuthLayout'
import { Alert, Button, Field, controlClass } from '../components/ui'
import { useAuth } from '../hooks/useAuth'
import { ROLE_LABEL } from '../lib/format'
import type { Role } from '../api/types'

const schema = z.object({
  email: z.string().min(3),
  password: z.string().min(8).max(72),
  role: z.enum(['ad_sales_executive', 'traffic_manager', 'ad_revenue_head']),
})

type FormValues = z.infer<typeof schema>

export function SignupPage() {
  const { signup } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { role: 'ad_sales_executive' },
  })

  return (
    <AuthLayout title="Create account" subtitle="All three roles can register and sign in immediately." footer={<span>Already registered? <AuthLink to="/login">Sign in</AuthLink></span>}>
      <form
        className="space-y-4"
        onSubmit={form.handleSubmit(async (values) => {
          setError(null)
          try {
            await signup(values.email, values.password, values.role as Role)
            navigate('/')
          } catch (err) {
            setError(err instanceof Error ? err.message : 'Sign up failed.')
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
        <Field label="Role">
          <select className={controlClass} {...form.register('role')}>
            {(Object.keys(ROLE_LABEL) as Role[]).map((role) => (
              <option key={role} value={role}>
                {ROLE_LABEL[role]}
              </option>
            ))}
          </select>
        </Field>
        <Button className="w-full" type="submit" disabled={form.formState.isSubmitting}>
          Create account
        </Button>
      </form>
    </AuthLayout>
  )
}
