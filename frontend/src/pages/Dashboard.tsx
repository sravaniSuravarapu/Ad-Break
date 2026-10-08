import { useQuery } from '@tanstack/react-query'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { api } from '../api/client'
import type { BreakSlot, DeliveryRow, FillRow, RevenueReport } from '../api/types'
import { Stat } from '../components/ui'
import { useTheme } from '../hooks/useTheme'
import { inr } from '../lib/format'

export function DashboardPage() {
  const { theme } = useTheme()
  const fill = useQuery({ queryKey: ['fill'], queryFn: () => api<FillRow[]>('/reports/fill') })
  const delivery = useQuery({ queryKey: ['delivery'], queryFn: () => api<DeliveryRow[]>('/reports/delivery') })
  const revenue = useQuery({ queryKey: ['revenue'], queryFn: () => api<RevenueReport>('/reports/revenue') })
  const openSlots = useQuery({ queryKey: ['availability'], queryFn: () => api<BreakSlot[]>('/availability') })

  const fillRows = fill.data ?? []
  const capacity = fillRows.reduce((sum, row) => sum + row.capacity_seconds, 0)
  const bookedSeconds = fillRows.reduce((sum, row) => sum + row.booked_seconds, 0)
  const avgFill = capacity ? (bookedSeconds / capacity) * 100 : 0
  const deliveryRows = delivery.data ?? []
  const aired = deliveryRows.reduce((sum, row) => sum + row.spots_aired, 0)
  const planned = deliveryRows.reduce((sum, row) => sum + row.planned_spots, 0)
  const avgDelivery = planned ? (aired / planned) * 100 : 0
  const revenueTotal = (revenue.data?.by_advertiser ?? []).reduce((sum, row) => sum + Number(row.revenue), 0)
  const openSeconds = (openSlots.data ?? []).reduce((sum, row) => sum + row.remaining_seconds, 0)
  const byDate = new Map<string, { date: string; booked: number; capacity: number }>()
  for (const row of fillRows) {
    const current = byDate.get(row.break_date) ?? { date: row.break_date.slice(5), booked: 0, capacity: 0 }
    current.booked += row.booked_seconds
    current.capacity += row.capacity_seconds
    byDate.set(row.break_date, current)
  }
  const chart = [...byDate.values()].map((row) => ({
    date: row.date,
    fill: row.capacity ? Math.round((row.booked / row.capacity) * 100) : 0,
  }))
  const bars = (revenue.data?.by_advertiser ?? []).map((row) => ({ name: row.name, revenue: Number(row.revenue) }))
  const axis = theme === 'dark' ? '#9aa3c7' : '#5d6787'
  const grid = theme === 'dark' ? 'rgba(255,255,255,0.06)' : '#e6eaf5'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold">Dashboard</h1>
        <p className="text-sm text-[var(--muted)]">Fill, delivery, and aired revenue for the current inventory.</p>
      </div>
      <section className="stagger grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Stat label="Break fill" value={`${avgFill.toFixed(1)}%`} hint="Booked seconds / capacity" tone="cyan" />
        <Stat label="Delivery" value={`${avgDelivery.toFixed(1)}%`} hint="Aired spots / planned spots" tone="accent" />
        <Stat label="Aired revenue" value={inr(revenueTotal)} hint="Aired spots × spot cost" tone="green" />
        <Stat label="Open seconds" value={openSeconds.toLocaleString()} hint="Remaining across listed breaks" tone="pink" />
      </section>
      <section className="grid gap-4 xl:grid-cols-[1.4fr_1fr]">
        <article className="rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4 shadow-[var(--shadow)]">
          <h2 className="mb-4 font-semibold">Fill by date</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chart}>
                <CartesianGrid stroke={grid} vertical={false} />
                <XAxis dataKey="date" stroke={axis} fontSize={12} />
                <YAxis stroke={axis} fontSize={12} />
                <Tooltip />
                <Bar dataKey="fill" fill={theme === 'dark' ? '#3ce0ff' : '#5b4dff'} radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
        <article className="rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4 shadow-[var(--shadow)]">
          <h2 className="mb-4 font-semibold">Revenue by advertiser</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={bars} layout="vertical" margin={{ left: 24 }}>
                <CartesianGrid stroke={grid} horizontal={false} />
                <XAxis type="number" stroke={axis} fontSize={12} />
                <YAxis type="category" dataKey="name" stroke={axis} fontSize={12} width={110} />
                <Tooltip />
                <Bar dataKey="revenue" fill={theme === 'dark' ? '#ff6b9d' : '#0c8f62'} radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
      </section>
    </div>
  )
}
