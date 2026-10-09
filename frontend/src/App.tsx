import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import { Shell } from './components/Shell'
import { useAuth } from './hooks/useAuth'
import { AdvertisersPage } from './pages/Advertisers'
import { AgenciesPage } from './pages/Agencies'
import { AvailabilityPage } from './pages/Availability'
import { BookingsPage } from './pages/Bookings'
import { BreaksPage } from './pages/Breaks'
import { CampaignsPage } from './pages/Campaigns'
import { DashboardPage } from './pages/Dashboard'
import { LoginPage } from './pages/Login'
import { RateCardPage } from './pages/RateCard'
import { ReportsPage } from './pages/Reports'
import { SignupPage } from './pages/Signup'
import type { Role } from './api/types'

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <p className="p-8 text-sm text-[var(--muted)]">Loading…</p>
  if (!user) return <Navigate to="/login" replace />
  return children
}

function RequireRole({ roles, children }: { roles: Role[]; children: ReactNode }) {
  const { user } = useAuth()
  if (!user || !roles.includes(user.role)) return <Navigate to="/" replace />
  return children
}

export function App() {
  const { user, loading } = useAuth()
  return (
    <Routes>
      <Route path="/login" element={user && !loading ? <Navigate to="/" replace /> : <LoginPage />} />
      <Route path="/signup" element={user && !loading ? <Navigate to="/" replace /> : <SignupPage />} />
      <Route element={<RequireAuth><Shell /></RequireAuth>}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/availability" element={<AvailabilityPage />} />
        <Route path="/bookings" element={<BookingsPage />} />
        <Route path="/campaigns" element={<RequireRole roles={['ad_sales_executive', 'ad_revenue_head']}><CampaignsPage /></RequireRole>} />
        <Route path="/advertisers" element={<RequireRole roles={['ad_sales_executive', 'ad_revenue_head']}><AdvertisersPage /></RequireRole>} />
        <Route path="/agencies" element={<RequireRole roles={['ad_sales_executive', 'ad_revenue_head']}><AgenciesPage /></RequireRole>} />
        <Route path="/breaks" element={<RequireRole roles={['traffic_manager']}><BreaksPage /></RequireRole>} />
        <Route path="/rate-card" element={<RequireRole roles={['ad_sales_executive', 'ad_revenue_head']}><RateCardPage /></RequireRole>} />
        <Route path="/reports" element={<ReportsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
