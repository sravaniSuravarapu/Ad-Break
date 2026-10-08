import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import type { Advertiser, Agency } from '../api/types'
import { Alert, Button, Field, controlClass } from '../components/ui'
import { useAuth } from '../hooks/useAuth'

export function AdvertisersPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const advertisers = useQuery({ queryKey: ['advertisers'], queryFn: () => api<Advertiser[]>('/advertisers') })
  const agencies = useQuery({ queryKey: ['agencies'], queryFn: () => api<Agency[]>('/agencies') })
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [agencyId, setAgencyId] = useState('')
  const [error, setError] = useState<string | null>(null)
  const sales = user?.role === 'ad_sales_executive'
  const save = useMutation({
    mutationFn: () =>
      api('/advertisers', {
        method: 'POST',
        body: JSON.stringify({ name, category, agency_id: agencyId || null }),
      }),
    onSuccess: async () => {
      setName('')
      setCategory('')
      setError(null)
      await queryClient.invalidateQueries({ queryKey: ['advertisers'] })
    },
    onError: (err: Error) => setError(err.message),
  })

  return (
    <div className="space-y-5">
      <h1 className="text-3xl font-extrabold">Advertisers</h1>
      {error && <Alert>{error}</Alert>}
      {sales && (
        <form className="grid gap-3 rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4 md:grid-cols-4" onSubmit={(event) => { event.preventDefault(); save.mutate() }}>
          <Field label="Name"><input className={controlClass} value={name} onChange={(event) => setName(event.target.value)} required /></Field>
          <Field label="Category"><input className={controlClass} value={category} onChange={(event) => setCategory(event.target.value)} required /></Field>
          <Field label="Agency">
            <select className={controlClass} value={agencyId} onChange={(event) => setAgencyId(event.target.value)}>
              <option value="">None</option>
              {(agencies.data ?? []).map((agency) => <option key={agency.id} value={agency.id}>{agency.name}</option>)}
            </select>
          </Field>
          <div className="flex items-end"><Button type="submit" disabled={save.isPending}>Add</Button></div>
        </form>
      )}
      <div className="grid gap-3 md:grid-cols-2">
        {(advertisers.data ?? []).map((item) => (
          <article key={item.id} className="rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4">
            <h2 className="font-semibold">{item.name}</h2>
            <p className="text-sm text-[var(--muted)]">{item.category}</p>
          </article>
        ))}
      </div>
    </div>
  )
}
