import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { useEffect } from 'react'

export function Button({
  variant = 'primary',
  className = '',
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary' | 'ghost' | 'danger' }) {
  const styles = {
    primary: 'bg-[var(--accent)] text-white hover:brightness-110',
    ghost: 'bg-transparent text-[var(--text)] border border-[var(--line)] hover:bg-[var(--accent-soft)]',
    danger: 'bg-[var(--pink)] text-white hover:brightness-110',
  }[variant]
  return (
    <button
      className={`inline-flex items-center justify-center rounded-xl px-4 py-2 text-sm font-semibold disabled:opacity-50 active:scale-[0.98] ${styles} ${className}`}
      {...props}
    />
  )
}

export function Field({
  label,
  children,
}: {
  label: string
  children: ReactNode
}) {
  return (
    <label className="block text-sm">
      <span className="mb-1.5 block font-medium text-[var(--muted)]">{label}</span>
      {children}
    </label>
  )
}

export const controlClass =
  'w-full rounded-xl border border-[var(--line)] bg-[var(--card-2)] px-3 py-2.5 text-sm text-[var(--text)] outline-none focus:border-[var(--accent)]'

export function Alert({ children }: { children: ReactNode }) {
  return (
    <p role="alert" className="rounded-xl bg-[color:color-mix(in_srgb,var(--pink)_16%,transparent)] px-3 py-2 text-sm text-[var(--pink)]">
      {children}
    </p>
  )
}

export function Modal({
  title,
  onClose,
  children,
}: {
  title: string
  onClose: () => void
  children: ReactNode
}) {
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div className="fixed inset-0 z-40 flex items-end justify-center bg-black/50 p-4 sm:items-center" onClick={onClose}>
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="modal-in max-h-[90vh] w-full max-w-lg overflow-auto rounded-3xl border border-[var(--line)] bg-[var(--card)] p-5 shadow-[var(--shadow)]"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">{title}</h2>
          <button className="text-sm text-[var(--muted)]" onClick={onClose} type="button">
            Close
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}

export function Stat({
  label,
  value,
  hint,
  tone = 'accent',
}: {
  label: string
  value: string
  hint: string
  tone?: 'accent' | 'cyan' | 'green' | 'pink'
}) {
  const toneClass = {
    accent: 'bg-[var(--accent)]',
    cyan: 'bg-[var(--cyan)]',
    green: 'bg-[var(--green)]',
    pink: 'bg-[var(--pink)]',
  }[tone]
  return (
    <article className="rounded-3xl border border-[var(--line)] bg-[var(--card)] p-4 shadow-[var(--shadow)] hover:-translate-y-0.5">
      <div className={`mb-4 h-1.5 w-10 rounded-full ${toneClass}`} />
      <p className="text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">{label}</p>
      <p className="mt-2 text-2xl font-extrabold">{value}</p>
      <p className="mt-1 text-sm text-[var(--muted)]">{hint}</p>
    </article>
  )
}

export function Pill({ children, tone = 'accent' }: { children: ReactNode; tone?: 'accent' | 'green' | 'pink' | 'amber' }) {
  const toneClass = {
    accent: 'bg-[var(--accent-soft)] text-[var(--accent)]',
    green: 'bg-[color:color-mix(in_srgb,var(--green)_18%,transparent)] text-[var(--green)]',
    pink: 'bg-[color:color-mix(in_srgb,var(--pink)_18%,transparent)] text-[var(--pink)]',
    amber: 'bg-[color:color-mix(in_srgb,var(--amber)_18%,transparent)] text-[var(--amber)]',
  }[tone]
  return <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${toneClass}`}>{children}</span>
}
