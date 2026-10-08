import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../hooks/useTheme'
import { ROLE_LABEL } from '../lib/format'
import type { Role } from '../api/types'

const ALL: Role[] = ['ad_sales_executive', 'traffic_manager', 'ad_revenue_head']

const NAV: { to: string; label: string; roles: Role[] }[] = [
  { to: '/', label: 'Dashboard', roles: ALL },
  { to: '/availability', label: 'Availability', roles: ALL },
  { to: '/bookings', label: 'Bookings', roles: ALL },
  { to: '/campaigns', label: 'Campaigns', roles: ALL },
  { to: '/advertisers', label: 'Advertisers', roles: ['ad_sales_executive', 'ad_revenue_head'] },
  { to: '/agencies', label: 'Agencies', roles: ['ad_sales_executive', 'ad_revenue_head'] },
  { to: '/breaks', label: 'Breaks', roles: ['traffic_manager'] },
  { to: '/rate-card', label: 'Rate card', roles: ALL },
  { to: '/reports', label: 'Reports', roles: ALL },
]

export function Shell() {
  const { user, logout } = useAuth()
  const { theme, toggle } = useTheme()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const items = NAV.filter((item) => user && item.roles.includes(user.role))

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[248px_1fr]">
      <aside
        className={`${open ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-30 flex w-[248px] flex-col border-r border-[var(--line)] bg-[var(--sidebar)] p-4 lg:static lg:translate-x-0`}
      >
        <div className="mb-8 flex items-center gap-3 px-2">
          <span className="grid h-10 w-10 place-items-center rounded-2xl text-sm font-extrabold text-white" style={{ background: 'var(--hero)' }}>
            AB
          </span>
          <div>
            <p className="font-extrabold">AdBreak</p>
            <p className="text-xs text-[var(--muted)]">Inventory desk</p>
          </div>
        </div>
        <nav className="flex flex-1 flex-col gap-1">
          {items.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `rounded-2xl px-3 py-2.5 text-sm font-semibold ${isActive ? 'bg-[var(--accent-soft)] text-[var(--accent)]' : 'text-[var(--muted)] hover:bg-[var(--card-2)] hover:text-[var(--text)]'}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <button
          className="mt-4 rounded-2xl px-3 py-2 text-left text-sm text-[var(--muted)] hover:bg-[var(--card-2)]"
          type="button"
          onClick={() => {
            logout()
            navigate('/login')
          }}
        >
          Sign out
        </button>
      </aside>
      {open && <button className="fixed inset-0 z-20 bg-black/40 lg:hidden" aria-label="Close menu" onClick={() => setOpen(false)} />}
      <div className="min-w-0">
        <header className="flex items-center justify-between gap-3 border-b border-[var(--line)] px-4 py-4 sm:px-6">
          <button className="rounded-xl border border-[var(--line)] px-3 py-2 text-sm lg:hidden" type="button" onClick={() => setOpen(true)}>
            Menu
          </button>
          <div className="hidden sm:block">
            <p className="text-sm text-[var(--muted)]">With live inventory, delivery, and revenue</p>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <button className="rounded-full border border-[var(--line)] px-3 py-1.5 text-sm font-semibold" type="button" onClick={toggle}>
              {theme === 'dark' ? 'Light' : 'Dark'}
            </button>
            <div className="rounded-full bg-[var(--card)] px-3 py-1.5 text-sm shadow-[var(--shadow)]">
              <span className="font-semibold">{user ? ROLE_LABEL[user.role] : ''}</span>
            </div>
          </div>
        </header>
        <main className="page-in p-4 sm:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
