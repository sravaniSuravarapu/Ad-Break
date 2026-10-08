import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { api } from '../api/client'
import type { Advertiser, Agency, Campaign, CampaignStatus } from '../api/types'
import { Alert, Button, Field, Pill, controlClass } from '../components/ui'
import { useAuth } from '../hooks/useAuth'
import { SPOT_LENGTHS, inr, titleCase } from '../lib/format'

const schema = z.object({
  advertiser_id: z.string().min(1),
  agency_id: z.string().optional(),
  name: z.string().min(1),
  start_date: z.string().min(1),
  end_date: z.string().min(1),
  spot_length: z.coerce.number(),
  planned_spots: z.coerce.number().int().positive(),
  budget: z.string().min(1),
})

type FormValues = z.infer<typeof schema>

export function CampaignsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const campaigns = useQuery({ queryKey: ['campaigns'], queryFn: () => api<Campaign[]>('/campaigns') })
  const advertisers = useQuery({ queryKey: ['advertisers'], queryFn: () => api<Advertiser[]>('/advertisers') })
  const agencies = useQuery({ queryKey: ['agencies'], queryFn: () => api<Agency[]>('/agencies') })
  const [error, setError] = useState<string | null>(null)
  const form = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: { spot_length: 30, planned_spots: 4, budget: '100000' } })
  const sales = user?.role === 'ad_sales_executive'
  const save = useMutation({
    mutationFn: (values: FormValues) =>
      api('/campaigns', {
        method: 'POST',
        body: JSON.stringify({ ...values, agency_id: values.agency_id || null }),
      }),
    onSuccess: async () => {
      setError(null)
      form.reset()
      await queryClient.invalidateQueries({ queryKey: ['campaigns'] })
    },
    onError: (err: Error) => setError(err.message),
  })
  const setStatus = useMutation({
    mutationFn: (input: { id: string; status: CampaignStatus }) =>
      api(`/campaigns/${input.id}/status`, { method: 'POST', body: JSON.stringify({ status: input.status }) }),
    onSuccess: async () => {
      setError(null)
      await queryClient.invalidateQueries({ queryKey: ['campaigns'] })
    },
    onError: (err: Error) => setError(err.message),
  })

  return (
    <div className="space-y-5">
      <h1 className="text-3xl font-extrabold">Campaigns</h1>
      {error && <Alert>{error}</Alert>}
      {sales && (
        <form className="grid gap-3 rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4 md:grid-cols-2" onSubmit={form.handleSubmit((values) => save.mutate(values))}>
          <Field label="Name"><input className={controlClass} {...form.register('name')} /></Field>
          <Field label="Advertiser">
            <select className={controlClass} {...form.register('advertiser_id')}>
              <option value="">Select</option>
              {(advertisers.data ?? []).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
          </Field>
          <Field label="Agency">
            <select className={controlClass} {...form.register('agency_id')}>
              <option value="">None</option>
              {(agencies.data ?? []).map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
          </Field>
          <Field label="Spot length">
            <select className={controlClass} {...form.register('spot_length')}>
              {SPOT_LENGTHS.map((length) => <option key={length} value={length}>{length}s</option>)}
            </select>
          </Field>
          <Field label="Start"><input className={controlClass} type="date" {...form.register('start_date')} /></Field>
          <Field label="End"><input className={controlClass} type="date" {...form.register('end_date')} /></Field>
          <Field label="Planned spots"><input className={controlClass} type="number" {...form.register('planned_spots')} /></Field>
          <Field label="Budget"><input className={controlClass} {...form.register('budget')} /></Field>
          <div className="md:col-span-2"><Button type="submit" disabled={save.isPending}>Create draft</Button></div>
        </form>
      )}
      <div className="grid gap-3">
        {(campaigns.data ?? []).map((campaign) => (
          <article key={campaign.id} className="rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="font-semibold">{campaign.name}</h2>
                <p className="text-sm text-[var(--muted)]">{campaign.advertiser_name} · {campaign.spot_length}s · {campaign.start_date} to {campaign.end_date}</p>
              </div>
              <Pill>{titleCase(campaign.status)}</Pill>
            </div>
            <p className="mt-3 text-sm text-[var(--muted)]">
              Aired {campaign.spots_aired}/{campaign.planned_spots} ({campaign.delivery_pct}%) · Budget {inr(campaign.booked_cost)} / {inr(campaign.budget)} ({campaign.budget_utilisation_pct}%)
            </p>
            {sales && (
              <div className="mt-3 flex flex-wrap gap-2">
                {campaign.status === 'draft' && <Button type="button" onClick={() => setStatus.mutate({ id: campaign.id, status: 'active' })}>Activate</Button>}
                {campaign.status === 'active' && <Button variant="ghost" type="button" onClick={() => setStatus.mutate({ id: campaign.id, status: 'completed' })}>Complete</Button>}
                {(campaign.status === 'draft' || campaign.status === 'active') && (
                  <Button variant="danger" type="button" onClick={() => setStatus.mutate({ id: campaign.id, status: 'cancelled' })}>Cancel campaign</Button>
                )}
              </div>
            )}
          </article>
        ))}
      </div>
    </div>
  )
}
