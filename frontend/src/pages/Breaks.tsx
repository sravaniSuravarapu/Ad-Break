import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import type { BreakSlot, Channel, Daypart } from '../api/types'
import { Alert, Button, Field, controlClass } from '../components/ui'
import { DAYPARTS, DAYPART_LABEL, clock } from '../lib/format'

export function BreaksPage() {
  const queryClient = useQueryClient()
  const channels = useQuery({ queryKey: ['channels'], queryFn: () => api<Channel[]>('/channels') })
  const breaks = useQuery({ queryKey: ['breaks'], queryFn: () => api<BreakSlot[]>('/breaks') })
  const [channelName, setChannelName] = useState('')
  const [channelId, setChannelId] = useState('')
  const [breakDate, setBreakDate] = useState('')
  const [startTime, setStartTime] = useState('20:00')
  const [daypart, setDaypart] = useState<Daypart>('prime')
  const [capacity, setCapacity] = useState('120')
  const [error, setError] = useState<string | null>(null)
  const saveChannel = useMutation({
    mutationFn: () => api('/channels', { method: 'POST', body: JSON.stringify({ name: channelName }) }),
    onSuccess: async () => {
      setChannelName('')
      setError(null)
      await queryClient.invalidateQueries({ queryKey: ['channels'] })
    },
    onError: (err: Error) => setError(err.message),
  })
  const saveBreak = useMutation({
    mutationFn: () =>
      api('/breaks', {
        method: 'POST',
        body: JSON.stringify({
          channel_id: channelId,
          break_date: breakDate,
          start_time: startTime.length === 5 ? `${startTime}:00` : startTime,
          daypart,
          capacity_seconds: Number(capacity),
        }),
      }),
    onSuccess: async () => {
      setError(null)
      await queryClient.invalidateQueries({ queryKey: ['breaks'] })
    },
    onError: (err: Error) => setError(err.message),
  })

  return (
    <div className="space-y-5">
      <h1 className="text-3xl font-extrabold">Breaks</h1>
      {error && <Alert>{error}</Alert>}
      <form className="flex flex-col gap-3 rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4 sm:flex-row sm:items-end" onSubmit={(event) => { event.preventDefault(); saveChannel.mutate() }}>
        <div className="flex-1"><Field label="New channel"><input className={controlClass} value={channelName} onChange={(event) => setChannelName(event.target.value)} required /></Field></div>
        <Button type="submit" disabled={saveChannel.isPending}>Add channel</Button>
      </form>
      <form className="grid gap-3 rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4 md:grid-cols-3" onSubmit={(event) => { event.preventDefault(); saveBreak.mutate() }}>
        <Field label="Channel">
          <select className={controlClass} value={channelId} required onChange={(event) => setChannelId(event.target.value)}>
            <option value="">Select</option>
            {(channels.data ?? []).map((channel) => <option key={channel.id} value={channel.id}>{channel.name}</option>)}
          </select>
        </Field>
        <Field label="Date"><input className={controlClass} type="date" value={breakDate} required onChange={(event) => setBreakDate(event.target.value)} /></Field>
        <Field label="Start"><input className={controlClass} type="time" value={startTime} required onChange={(event) => setStartTime(event.target.value)} /></Field>
        <Field label="Daypart">
          <select className={controlClass} value={daypart} onChange={(event) => setDaypart(event.target.value as Daypart)}>
            {DAYPARTS.map((item) => <option key={item} value={item}>{DAYPART_LABEL[item]}</option>)}
          </select>
        </Field>
        <Field label="Capacity seconds"><input className={controlClass} value={capacity} onChange={(event) => setCapacity(event.target.value)} /></Field>
        <div className="flex items-end"><Button type="submit" disabled={saveBreak.isPending}>Add break</Button></div>
      </form>
      <div className="overflow-auto rounded-3xl border border-[var(--line)] bg-[var(--card)]">
        <table className="min-w-full text-left text-sm">
          <thead className="text-[var(--muted)]"><tr>{['Channel', 'When', 'Daypart', 'Remaining'].map((heading) => <th key={heading} className="px-4 py-3 font-medium">{heading}</th>)}</tr></thead>
          <tbody>
            {(breaks.data ?? []).map((item) => (
              <tr key={item.id} className="border-t border-[var(--line)]">
                <td className="px-4 py-3">{item.channel_name}</td>
                <td className="px-4 py-3">{item.break_date} {clock(item.start_time)}</td>
                <td className="px-4 py-3">{DAYPART_LABEL[item.daypart]}</td>
                <td className="px-4 py-3">{item.remaining_seconds}s / {item.capacity_seconds}s</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
