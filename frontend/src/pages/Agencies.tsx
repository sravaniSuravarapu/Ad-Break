import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import type { Agency } from '../api/types'
import { Alert, Button, Field, controlClass } from '../components/ui'
import { useAuth } from '../hooks/useAuth'

export function AgenciesPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const agencies = useQuery({ queryKey: ['agencies'], queryFn: () => api<Agency[]>('/agencies') })
  const [name, setName] = useState('')
  const [error, setError] = useState<string | null>(null)
  const save = useMutation({
    mutationFn: () => api('/agencies', { method: 'POST', body: JSON.stringify({ name }) }),
    onSuccess: async () => {
      setName('')
      setError(null)
      await queryClient.invalidateQueries({ queryKey: ['agencies'] })
    },
    onError: (err: Error) => setError(err.message),
  })

  return (
    <div className="space-y-5">
      <h1 className="text-3xl font-extrabold">Agencies</h1>
      {error && <Alert>{error}</Alert>}
      {user?.role === 'ad_sales_executive' && (
        <form className="flex flex-col gap-3 rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4 sm:flex-row sm:items-end" onSubmit={(event) => { event.preventDefault(); save.mutate() }}>
          <div className="flex-1"><Field label="Name"><input className={controlClass} value={name} onChange={(event) => setName(event.target.value)} required /></Field></div>
          <Button type="submit" disabled={save.isPending}>Add agency</Button>
        </form>
      )}
      <div className="grid gap-3 md:grid-cols-2">
        {(agencies.data ?? []).map((agency) => (
          <article key={agency.id} className="rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4 font-semibold">{agency.name}</article>
        ))}
      </div>
    </div>
  )
}
