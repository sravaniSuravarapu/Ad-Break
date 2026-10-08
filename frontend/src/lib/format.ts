import type { BookingStatus, CampaignStatus, Daypart, Role } from '../api/types'

export const ROLE_LABEL: Record<Role, string> = {
  ad_sales_executive: 'Ad Sales Executive',
  traffic_manager: 'Traffic Manager',
  ad_revenue_head: 'Ad Revenue Head',
}

export const DAYPART_LABEL: Record<Daypart, string> = {
  morning: 'Morning',
  daytime: 'Daytime',
  prime: 'Prime',
  late_night: 'Late night',
}

export const DAYPARTS: Daypart[] = ['morning', 'daytime', 'prime', 'late_night']
export const SPOT_LENGTHS = [10, 15, 20, 30, 60]

export function titleCase(value: CampaignStatus | BookingStatus | string): string {
  return value.replaceAll('_', ' ').replace(/^\w/, (letter) => letter.toUpperCase())
}

export function inr(value: string | number): string {
  const amount = typeof value === 'number' ? value : Number(value)
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(Number.isFinite(amount) ? amount : 0)
}

export function when(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

export function clock(value: string): string {
  return value.slice(0, 5)
}
