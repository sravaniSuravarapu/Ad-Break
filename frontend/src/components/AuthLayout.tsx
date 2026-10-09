import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useTheme } from '../hooks/useTheme'

export function AuthLayout({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string
  subtitle: string
  children: ReactNode
  footer: ReactNode
}) {
  const { theme, toggle } = useTheme()
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <section className="hero-live relative hidden overflow-hidden p-10 text-white lg:flex lg:flex-col lg:justify-between">
        <p className="text-sm font-semibold tracking-wide">AdBreak</p>
        <div className="page-in">
          <h1 className="max-w-md text-5xl font-extrabold leading-tight">Book the break. Keep the promise.</h1>
          <p className="mt-4 max-w-sm text-white/85">Capacity, competitors, budgets, and as-run delivery in one desk.</p>
        </div>
        <p className="text-sm text-white/75">Adapted from the RecehTok dashboard layout for television inventory.</p>
      </section>
      <section className="flex items-center justify-center bg-[var(--bg)] p-6">
        <div className="page-in w-full max-w-md rounded-3xl border border-[var(--line)] bg-[var(--card)] p-6 shadow-[var(--shadow)]">
          <div className="mb-6 flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-extrabold">{title}</h2>
              <p className="mt-1 text-sm text-[var(--muted)]">{subtitle}</p>
            </div>
            <button className="rounded-full border border-[var(--line)] px-3 py-1 text-sm" type="button" onClick={toggle}>
              {theme === 'dark' ? 'Light' : 'Dark'}
            </button>
          </div>
          {children}
          <div className="mt-4 text-sm text-[var(--muted)]">{footer}</div>
        </div>
      </section>
    </div>
  )
}

export function AuthLink({ to, children }: { to: string; children: ReactNode }) {
  return (
    <Link className="font-semibold text-[var(--accent)]" to={to}>
      {children}
    </Link>
  )
}
