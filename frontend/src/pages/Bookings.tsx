import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import type { Booking, BreakSlot } from '../api/types'
import { Alert, Button, Field, Modal, Pill, controlClass } from '../components/ui'
import { useAuth } from '../hooks/useAuth'
import { DAYPART_LABEL, clock, inr, titleCase } from '../lib/format'

export function BookingsPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const bookings = useQuery({ queryKey: ['bookings'], queryFn: () => api<Booking[]>('/bookings') })
  const slots = useQuery({ queryKey: ['availability'], queryFn: () => api<BreakSlot[]>('/availability') })
  const [moveId, setMoveId] = useState<string | null>(null)
  const [rebookId, setRebookId] = useState<string | null>(null)
  const [breakId, setBreakId] = useState('')
  const [error, setError] = useState<string | null>(null)
  const refresh = async () => {
    setError(null)
    await queryClient.invalidateQueries()
  }
  const act = useMutation({
    mutationFn: async (action: { path: string; body?: unknown }) =>
      api(action.path, { method: 'POST', body: action.body ? JSON.stringify(action.body) : undefined }),
    onSuccess: async () => {
      setMoveId(null)
      setRebookId(null)
      await refresh()
    },
    onError: (err: Error) => setError(err.message),
  })
  const sales = user?.role === 'ad_sales_executive'
  const traffic = user?.role === 'traffic_manager'

  return (
    <div className="space-y-5">
      <h1 className="text-3xl font-extrabold">Bookings</h1>
      {error && <Alert>{error}</Alert>}
      <div className="overflow-auto rounded-3xl border border-[var(--line)] bg-[var(--card)]">
        <table className="min-w-full text-left text-sm">
          <thead className="text-[var(--muted)]">
            <tr>
              {['Campaign', 'Advertiser', 'Break', 'Cost', 'Status', ''].map((heading) => (
                <th key={heading} className="px-4 py-3 font-medium">{heading}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(bookings.data ?? []).map((booking) => (
              <tr key={booking.id} className="border-t border-[var(--line)]">
                <td className="px-4 py-3 font-semibold">{booking.campaign_name}</td>
                <td className="px-4 py-3">{booking.advertiser_name}<div className="text-xs text-[var(--muted)]">{booking.category}</div></td>
                <td className="px-4 py-3">{booking.channel_name}<div className="text-xs text-[var(--muted)]">{booking.break_date} {clock(booking.start_time)} · {DAYPART_LABEL[booking.daypart]}</div></td>
                <td className="px-4 py-3">{inr(booking.cost)}</td>
                <td className="px-4 py-3"><Pill tone={booking.status === 'aired' ? 'green' : booking.status === 'missed' || booking.status === 'cancelled' ? 'pink' : 'accent'}>{titleCase(booking.status)}</Pill></td>
                <td className="space-x-2 px-4 py-3 text-right">
                  {sales && booking.status === 'booked' && (
                    <>
                      <Button variant="ghost" type="button" onClick={() => act.mutate({ path: `/bookings/${booking.id}/cancel` })}>Cancel</Button>
                      <Button variant="ghost" type="button" onClick={() => { setMoveId(booking.id); setError(null) }}>Move</Button>
                    </>
                  )}
                  {sales && booking.status === 'cancelled' && (
                    <Button variant="ghost" type="button" onClick={() => { setRebookId(booking.id); setError(null) }}>Rebook</Button>
                  )}
                  {traffic && booking.status === 'booked' && (
                    <>
                      <Button type="button" onClick={() => act.mutate({ path: `/bookings/${booking.id}/as-run`, body: { status: 'aired' } })}>Aired</Button>
                      <Button variant="ghost" type="button" onClick={() => act.mutate({ path: `/bookings/${booking.id}/as-run`, body: { status: 'missed' } })}>Missed</Button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {(moveId || rebookId) && (
        <Modal title={moveId ? 'Move booking' : 'Rebook'} onClose={() => { setMoveId(null); setRebookId(null) }}>
          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault()
              const id = moveId ?? rebookId
              act.mutate({
                path: `/bookings/${id}/${moveId ? 'move' : 'rebook'}`,
                body: { ad_break_id: breakId },
              })
            }}
          >
            {error && <Alert>{error}</Alert>}
            <Field label="Break">
              <select className={controlClass} value={breakId} required onChange={(event) => setBreakId(event.target.value)}>
                <option value="">Select</option>
                {(slots.data ?? []).map((slot) => (
                  <option key={slot.id} value={slot.id}>
                    {slot.channel_name} {slot.break_date} {clock(slot.start_time)} · {slot.remaining_seconds}s left
                  </option>
                ))}
              </select>
            </Field>
            <Button type="submit" disabled={act.isPending || !breakId}>{moveId ? 'Move' : 'Rebook'}</Button>
          </form>
        </Modal>
      )}
    </div>
  )
}
