import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import type { DeliveryRow, FillRow, RevenueReport } from '../api/types'
import { DAYPART_LABEL, inr } from '../lib/format'

function MoneyTable({ title, rows }: { title: string; rows: { name: string; revenue: string }[] }) {
  return (
    <article className="rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4">
      <h2 className="mb-3 font-semibold">{title}</h2>
      <ul className="space-y-2 text-sm">
        {rows.length === 0 && <li className="text-[var(--muted)]">No aired revenue yet.</li>}
        {rows.map((row) => (
          <li key={row.name} className="flex justify-between gap-3">
            <span>{row.name}</span>
            <span className="font-semibold">{inr(row.revenue)}</span>
          </li>
        ))}
      </ul>
    </article>
  )
}

export function ReportsPage() {
  const fill = useQuery({ queryKey: ['fill'], queryFn: () => api<FillRow[]>('/reports/fill') })
  const delivery = useQuery({ queryKey: ['delivery'], queryFn: () => api<DeliveryRow[]>('/reports/delivery') })
  const revenue = useQuery({ queryKey: ['revenue'], queryFn: () => api<RevenueReport>('/reports/revenue') })

  return (
    <div className="space-y-5">
      <h1 className="text-3xl font-extrabold">Reports</h1>
      <section className="overflow-auto rounded-3xl border border-[var(--line)] bg-[var(--card)]">
        <table className="min-w-full text-left text-sm">
          <thead className="text-[var(--muted)]"><tr>{['Channel', 'Date', 'Daypart', 'Fill'].map((heading) => <th key={heading} className="px-4 py-3 font-medium">{heading}</th>)}</tr></thead>
          <tbody>
            {(fill.data ?? []).map((row) => (
              <tr key={`${row.channel_id}-${row.break_date}-${row.daypart}`} className="border-t border-[var(--line)]">
                <td className="px-4 py-3">{row.channel_name}</td>
                <td className="px-4 py-3">{row.break_date}</td>
                <td className="px-4 py-3">{DAYPART_LABEL[row.daypart]}</td>
                <td className="px-4 py-3">{row.booked_seconds}/{row.capacity_seconds}s · {row.fill_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <section className="overflow-auto rounded-3xl border border-[var(--line)] bg-[var(--card)]">
        <table className="min-w-full text-left text-sm">
          <thead className="text-[var(--muted)]"><tr>{['Campaign', 'Delivery', 'Budget'].map((heading) => <th key={heading} className="px-4 py-3 font-medium">{heading}</th>)}</tr></thead>
          <tbody>
            {(delivery.data ?? []).map((row) => (
              <tr key={row.campaign_id} className="border-t border-[var(--line)]">
                <td className="px-4 py-3">{row.campaign_name}<div className="text-xs text-[var(--muted)]">{row.advertiser_name}</div></td>
                <td className="px-4 py-3">{row.spots_aired}/{row.planned_spots} · {row.delivery_pct}%</td>
                <td className="px-4 py-3">{inr(row.booked_cost)} / {inr(row.budget)} · {row.budget_utilisation_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <section className="grid gap-4 lg:grid-cols-3">
        <MoneyTable title="By advertiser" rows={revenue.data?.by_advertiser ?? []} />
        <MoneyTable title="By category" rows={revenue.data?.by_category ?? []} />
        <MoneyTable title="By channel" rows={revenue.data?.by_channel ?? []} />
      </section>
    </div>
  )
}
