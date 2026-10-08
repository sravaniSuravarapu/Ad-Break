import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import type { Daypart, RateCard } from '../api/types'
import { Alert, Button, controlClass } from '../components/ui'
import { useAuth } from '../hooks/useAuth'
import { DAYPARTS, DAYPART_LABEL, inr } from '../lib/format'

export function RateCardPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const rates = useQuery({ queryKey: ['rate-card'], queryFn: () => api<RateCard[]>('/rate-card') })
  const [drafts, setDrafts] = useState<Partial<Record<Daypart, string>>>({})
  const [error, setError] = useState<string | null>(null)
  const save = useMutation({
    mutationFn: (input: { daypart: Daypart; rate: string }) =>
      api(`/rate-card/${input.daypart}`, { method: 'PUT', body: JSON.stringify({ rate_per_10s: input.rate }) }),
    onSuccess: async () => {
      setError(null)
      setDrafts({})
      await queryClient.invalidateQueries({ queryKey: ['rate-card'] })
    },
    onError: (err: Error) => setError(err.message),
  })
  const byDaypart = new Map((rates.data ?? []).map((row) => [row.daypart, row]))
  const canEdit = user?.role === 'ad_revenue_head'

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-3xl font-extrabold">Rate card</h1>
        <p className="text-sm text-[var(--muted)]">Price per 10 seconds. Bookings read these rates from the API.</p>
      </div>
      {error && <Alert>{error}</Alert>}
      <div className="stagger grid gap-4 md:grid-cols-2">
        {DAYPARTS.map((daypart) => {
          const current = byDaypart.get(daypart)
          const value = drafts[daypart] ?? current?.rate_per_10s ?? ''
          return (
            <article key={daypart} className="rounded-3xl border border-[var(--line)] bg-[var(--card)] p-5">
              <p className="text-sm text-[var(--muted)]">{DAYPART_LABEL[daypart]}</p>
              <p className="mt-2 text-2xl font-extrabold">{current ? inr(current.rate_per_10s) : 'Not set'}</p>
              <p className="text-xs text-[var(--muted)]">per 10 seconds</p>
              {canEdit && (
                <form
                  className="mt-4 flex gap-2"
                  onSubmit={(event) => {
                    event.preventDefault()
                    save.mutate({ daypart, rate: value })
                  }}
                >
                  <input className={controlClass} value={value} onChange={(event) => setDrafts((prev) => ({ ...prev, [daypart]: event.target.value }))} />
                  <Button type="submit" disabled={save.isPending}>Save</Button>
                </form>
              )}
            </article>
          )
        })}
      </div>
    </div>
  )
}
