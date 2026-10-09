import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { useTheme } from '../hooks/useTheme'
import { ROLE_LABEL } from '../lib/format'
import type { Role } from '../api/types'

const ALL: Role[] = ['ad_sales_executive', 'traffic_manager', 'ad_revenue_head']
const SALES_REVENUE: Role[] = ['ad_sales_executive', 'ad_revenue_head']

const NAV: { to: string; label: string; roles: Role[] }[] = [
  { to: '/', label: 'Dashboard', roles: ALL },
  { to: '/availability', label: 'Availability', roles: ALL },
  { to: '/bookings', label: 'Bookings', roles: ALL },
  { to: '/campaigns', label: 'Campaigns', roles: SALES_REVENUE },
  { to: '/advertisers', label: 'Advertisers', roles: SALES_REVENUE },
  { to: '/agencies', label: 'Agencies', roles: SALES_REVENUE },
  { to: '/breaks', label: 'Breaks', roles: ['traffic_manager'] },
  { to: '/rate-card', label: 'Rate card', roles: SALES_REVENUE },
  { to: '/reports', label: 'Reports', roles: ALL },
]

export function Shell() {
  const { user, logout } = useAuth()
  const { theme, toggle } = useTheme()
  const navigate = useNavigate()
  const [open, setOpen] = useState(() => window.matchMedia('(min-width: 1024px)').matches)
  const items = NAV.filter((item) => user && item.roles.includes(user.role))

  return (
    <div className="min-h-screen">
      <aside
        id="app-sidebar"
        aria-hidden={!open}
        className={`sidebar-panel fixed inset-y-0 left-0 z-30 flex w-[248px] flex-col border-r border-[var(--line)] bg-[var(--sidebar)] p-4 ${open ? 'translate-x-0' : 'pointer-events-none -translate-x-full'}`}
      >
        <div className="mb-8 flex items-center gap-3 px-2">
          <span className="mark grid h-10 w-10 place-items-center rounded-2xl text-sm font-extrabold text-white">
            AB
          </span>
          <div>
            <p className="font-extrabold">AdBreak</p>
            <p className="text-xs text-[var(--muted)]">Inventory desk</p>
          </div>
        </div>
        <nav className="flex flex-1 flex-col gap-1">
          {items.map((item, index) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              tabIndex={open ? 0 : -1}
              onClick={() => {
                if (window.matchMedia('(max-width: 1023px)').matches) setOpen(false)
              }}
              style={{ animationDelay: `${index * 45}ms` }}
              className={({ isActive }) =>
                `nav-link rounded-2xl px-3 py-2.5 text-sm font-semibold ${isActive ? 'bg-[var(--accent-soft)] text-[var(--accent)]' : 'text-[var(--muted)] hover:bg-[var(--card-2)] hover:text-[var(--text)]'}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <button
          className="mt-4 rounded-2xl px-3 py-2 text-left text-sm text-[var(--muted)] hover:bg-[var(--card-2)]"
          type="button"
          tabIndex={open ? 0 : -1}
          onClick={() => {
            logout()
            navigate('/login')
          }}
        >
          Sign out
        </button>
      </aside>
      {open && (
        <button
          className="fixed inset-0 z-20 bg-black/40 lg:hidden"
          aria-label="Close sidebar"
          onClick={() => setOpen(false)}
        />
      )}
      <div className={`sidebar-shift min-w-0 ${open ? 'lg:ml-[248px]' : 'lg:ml-0'}`}>
        <header className="flex items-center justify-between gap-3 border-b border-[var(--line)] px-4 py-4 sm:px-6">
          <button
            className="rounded-xl border border-[var(--line)] px-3 py-2 text-sm font-semibold"
            type="button"
            aria-expanded={open}
            aria-controls="app-sidebar"
            onClick={() => setOpen((value) => !value)}
          >
            {open ? 'Hide' : 'Menu'}
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
