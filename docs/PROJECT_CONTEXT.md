# Project: Ad Break & Campaign Booking Manager

## Description
Advertising inventory management system for television channels. Manage
advertisers, campaigns, budgets, ad break inventories and booking
schedules. Validate break capacity, prevent competitor advertisements in
the same break, enforce campaign budgets, and track delivery against
commitments. Include revenue reports, airtime utilization dashboards,
campaign performance tracking, and availability search so sales teams
can quickly find open slots.

## Roles
- Ad Sales Executive: sells and books spots.
- Traffic Manager: creates breaks, marks Aired/Missed.
- Ad Revenue Head: revenue, fill rate, campaign delivery.

## Business Expectations
Sales users expect to quickly find available airtime, create campaigns,
and book spots while seeing available break capacity. The system must
prevent overbooking, competitor conflicts and bookings beyond campaign
budgets. Managers expect real-time visibility into campaign delivery,
break utilization, available inventory and revenue.

## As-Is Process
1. Agency sends a Release Order (RO) by email with dates, spot length, number of spots and budget.
2. Sales executive checks availability in a shared Excel inventory per channel/date.
3. Spots are typed into the break sheet; two executives may book the same seconds.
4. Traffic Manager builds the final break log, fixes overbookings and competitor clashes by moving spots.
5. After airing, traffic marks what aired; missed spots need make-goods.
6. Revenue and delivery reports compiled manually at month end.

## Pain Points
- Overbooked breaks force dropped spots, make-goods, lost revenue.
- Unsold breaks mean lost revenue.
- Competitor clashes breach advertiser contracts.
- Budgets exceeded without notice.
- No real-time view of inventory or campaign delivery.

## To-Be Process
1. Sales exec creates advertiser (with category) and campaign (dates, spot length, planned spots, budget).
2. Availability search shows breaks by channel/date/daypart with remaining seconds.
3. Booking validates capacity, one spot per advertiser per break, competitor category, budget and planned spots; failures show reason and remaining seconds.
4. Traffic Manager maintains breaks and marks spots Aired/Missed after airing.
5. Dashboards: break fill %, campaign delivery (aired vs planned), revenue by advertiser.

## Personas
- Ad Sales Executive (Rahul): books 50-100 spots a day; needs quick availability search and instant validation.
- Traffic Manager (Swati): creates next week's break inventory and confirms as-run each morning.
- Ad Revenue Head (Ms. Menon): daily revenue and fill-rate view; weekly campaign delivery review with key accounts.

## Glossary
- Ad break: commercial pause with capacity in seconds.
- Spot: one ad of fixed length (10/15/20/30/60 s).
- Release Order (RO): advertiser's booking instruction.
- Daypart: Morning, Daytime, Prime 19:00-23:00, Late night.
- Rate card: price per 10 seconds per daypart.
- Competitor clash: two advertisers of the same category in one break.
- As-run: confirmation of what actually aired.
- Make-good: free replacement for a missed spot.

## Business Rules
- BR-01 Campaign end date >= start date; spot length in {10, 15, 20, 30, 60} s.
- BR-02 Break date within campaign dates.
- BR-03 Booked seconds in a break <= break capacity (default 120 s); rejection shows remaining seconds.
- BR-04 Max one spot per advertiser per break.
- BR-05 No two advertisers of the same category in the same break.
- BR-06 Spot cost = (spot length / 10) x rate per 10 s for the break's daypart; total booked cost <= campaign budget.
- BR-07 Booked spots <= planned spots.
- BR-08 Cancelled/completed campaigns cannot be booked.
- BR-09 Only Traffic Manager creates breaks and marks Aired/Missed; booking can be cancelled only before break date.
- BR-10 Capacity check done in a transaction so two simultaneous bookings cannot overbook.

## Statuses
- Campaign: Draft -> Active -> Completed | Cancelled.
- Booking: Booked -> Aired | Missed | Cancelled.

## KPIs
- Break fill % = booked seconds / capacity (by channel/date/daypart).
- Campaign delivery % = aired spots / planned spots; booked vs planned.
- Budget utilisation % = booked cost / budget.
- Revenue by advertiser/category/channel = aired spots x spot cost.

## Data, Privacy, Compliance
Fictional advertisers and rates. Keep booking history including cancellations.

## Non-Functional
Availability search < 2 s for 7 days x 3 channels x 20 breaks; concurrency-safe booking.

## In Scope (5-day MVP)
Login and roles, advertisers, campaigns, ad breaks, availability search, booking with all validations, as-run marking, 3 reports/dashboard.

## Out of Scope
Agency commissions, invoicing, programmatic/digital ads, automatic optimisation, make-good automation, integration with playout (P6).

## Gaps Added to Original Brief
Advertiser category and competitor rule (BR-05), budget formula with rate card (BR-06), as-run marking and delivery (BR-09), concurrency rule (BR-10), campaign/booking statuses, dayparts.
