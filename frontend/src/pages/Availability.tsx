import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import type { BreakSlot, Campaign, Channel } from '../api/types'
import { Alert, Button, Field, Modal, Pill, controlClass } from '../components/ui'
import { useAuth } from '../hooks/useAuth'
import { DAYPARTS, DAYPART_LABEL, clock } from '../lib/format'

export function AvailabilityPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const channels = useQuery({ queryKey: ['channels'], queryFn: () => api<Channel[]>('/channels') })
  const campaigns = useQuery({ queryKey: ['campaigns'], queryFn: () => api<Campaign[]>('/campaigns') })
  const [channelId, setChannelId] = useState('')
  const [daypart, setDaypart] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const params = new URLSearchParams()
  if (channelId) params.set('channel_id', channelId)
  if (daypart) params.set('daypart', daypart)
  if (dateFrom) params.set('date_from', dateFrom)
  if (dateTo) params.set('date_to', dateTo)
  const slots = useQuery({
    queryKey: ['availability', params.toString()],
    queryFn: () => api<BreakSlot[]>(`/availability?${params.toString()}`),
  })
  const [target, setTarget] = useState<BreakSlot | null>(null)
  const [campaignId, setCampaignId] = useState('')
  const [error, setError] = useState<string | null>(null)
  const book = useMutation({
    mutationFn: () =>
      api('/bookings', {
        method: 'POST',
        body: JSON.stringify({ campaign_id: campaignId, ad_break_id: target?.id }),
      }),
    onSuccess: async () => {
      setTarget(null)
      setError(null)
      await queryClient.invalidateQueries()
    },
    onError: (err: Error) => setError(err.message),
  })
  const active = (campaigns.data ?? []).filter((item) => item.status === 'active')

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-3xl font-extrabold">Availability</h1>
        <p className="text-sm text-[var(--muted)]">Open seconds come from the inventory API.</p>
      </div>
      <div className="grid gap-3 rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4 md:grid-cols-4">
        <Field label="Channel">
          <select className={controlClass} value={channelId} onChange={(event) => setChannelId(event.target.value)}>
            <option value="">All</option>
            {(channels.data ?? []).map((channel) => (
              <option key={channel.id} value={channel.id}>{channel.name}</option>
            ))}
          </select>
        </Field>
        <Field label="Daypart">
          <select className={controlClass} value={daypart} onChange={(event) => setDaypart(event.target.value)}>
            <option value="">All</option>
            {DAYPARTS.map((item) => (
              <option key={item} value={item}>{DAYPART_LABEL[item]}</option>
            ))}
          </select>
        </Field>
        <Field label="From"><input className={controlClass} type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} /></Field>
        <Field label="To"><input className={controlClass} type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} /></Field>
      </div>
      <div className="overflow-auto rounded-3xl border border-[var(--line)] bg-[var(--card)]">
        <table className="min-w-full text-left text-sm">
          <thead className="text-[var(--muted)]">
            <tr>
              {['Channel', 'Date', 'Time', 'Daypart', 'Remaining', 'Fill', ''].map((heading) => (
                <th key={heading} className="px-4 py-3 font-medium">{heading}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(slots.data ?? []).map((slot) => (
              <tr key={slot.id} className="border-t border-[var(--line)]">
                <td className="px-4 py-3 font-semibold">{slot.channel_name}</td>
                <td className="px-4 py-3">{slot.break_date}</td>
                <td className="px-4 py-3">{clock(slot.start_time)}</td>
                <td className="px-4 py-3">{DAYPART_LABEL[slot.daypart]}</td>
                <td className="px-4 py-3">{slot.remaining_seconds}s</td>
                <td className="px-4 py-3"><Pill>{slot.fill_pct}%</Pill></td>
                <td className="px-4 py-3 text-right">
                  {user?.role === 'ad_sales_executive' && (
                    <Button type="button" onClick={() => { setTarget(slot); setError(null) }}>Book</Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {target && (
        <Modal title={`Book ${target.channel_name}`} onClose={() => setTarget(null)}>
          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault()
              book.mutate()
            }}
          >
            {error && <Alert>{error}</Alert>}
            <p className="text-sm text-[var(--muted)]">{target.remaining_seconds} seconds remaining in this break.</p>
            <Field label="Active campaign">
              <select className={controlClass} value={campaignId} onChange={(event) => setCampaignId(event.target.value)} required>
                <option value="">Select</option>
                {active.map((campaign) => (
                  <option key={campaign.id} value={campaign.id}>
                    {campaign.name} · {campaign.spot_length}s · {campaign.advertiser_name}
                  </option>
                ))}
              </select>
            </Field>
            <Button type="submit" disabled={book.isPending || !campaignId}>Confirm booking</Button>
          </form>
        </Modal>
      )}
    </div>
  )
}
