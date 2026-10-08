export type Role = 'ad_sales_executive' | 'traffic_manager' | 'ad_revenue_head'
export type Daypart = 'morning' | 'daytime' | 'prime' | 'late_night'
export type CampaignStatus = 'draft' | 'active' | 'completed' | 'cancelled'
export type BookingStatus = 'booked' | 'aired' | 'missed' | 'cancelled'

export interface User {
  id: string
  email: string
  role: Role
  is_active: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Agency {
  id: string
  name: string
  created_at: string
  updated_at: string
}

export interface Advertiser {
  id: string
  name: string
  category: string
  agency_id: string | null
  created_at: string
}

export interface Campaign {
  id: string
  advertiser_id: string
  advertiser_name: string
  agency_id: string | null
  name: string
  start_date: string
  end_date: string
  spot_length: number
  planned_spots: number
  budget: string
  status: CampaignStatus
  spots_booked: number
  spots_aired: number
  spots_missed: number
  spots_counting: number
  booked_cost: string
  delivery_pct: number
  budget_utilisation_pct: number
  created_at: string
}

export interface Channel {
  id: string
  name: string
}

export interface RateCard {
  daypart: Daypart
  rate_per_10s: string
  updated_at: string
}

export interface BreakSlot {
  id: string
  channel_id: string
  channel_name: string
  break_date: string
  start_time: string
  daypart: Daypart
  capacity_seconds: number
  booked_seconds: number
  remaining_seconds: number
  fill_pct: number
}

export interface Booking {
  id: string
  campaign_id: string
  campaign_name: string
  advertiser_name: string
  category: string
  ad_break_id: string
  channel_name: string
  break_date: string
  start_time: string
  daypart: Daypart
  spot_length: number
  cost: string
  status: BookingStatus
  created_at: string
  remaining_seconds: number
}

export interface FillRow {
  channel_id: string
  channel_name: string
  break_date: string
  daypart: Daypart
  capacity_seconds: number
  booked_seconds: number
  fill_pct: number
}

export interface DeliveryRow {
  campaign_id: string
  campaign_name: string
  advertiser_name: string
  planned_spots: number
  spots_aired: number
  spots_counting: number
  delivery_pct: number
  budget: string
  booked_cost: string
  budget_utilisation_pct: number
}

export interface RevenueRow {
  name: string
  revenue: string
}

export interface RevenueReport {
  by_advertiser: RevenueRow[]
  by_category: RevenueRow[]
  by_channel: RevenueRow[]
}
