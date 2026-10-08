| # | Question | Answer | Status |
|---|----------|--------|--------|
| 1 | Confirm rate card per daypart values for demo seed data. | | Open |
| 2 | Category conflict rule: exact category match only? | | Open |
| 3 | Can a booking be moved to another break (or cancel + rebook)? | | Open |
| 4 | Is Agency an entity for MVP? | | Open |
| 5 | Timestamps: created_at and updated_at (UTC) on every table, plus bookings.created_at and booking_status_history.changed_at? | | Open |
| 6 | created_by and changed_by: non-null UUID foreign keys to users.id? | | Open |
| 7 | booking_status_history.old_status nullable? | | Open |
| 8 | Unique constraints beyond users.email and ad_breaks (channel + date + start_time)? Specifically rate_card.daypart, channels.name, advertisers.name? | | Open |
| 9 | Enum values: ad_sales_executive, traffic_manager, ad_revenue_head; morning, daytime, prime, late_night; campaign draft, active, completed, cancelled; booking booked, aired, missed, cancelled? | | Open |
| 10 | Add uvicorn to backend dependencies so the API can start? | | Open |
| 11 | Compose defaults: Postgres 16, db/user/password adbreak, host port 5432, API port 8000, API DATABASE_URL host postgres, .env.example uses localhost? | | Open |
| 12 | Figma Dev link for UI (not provided yet). | | Open |
| 13 | Sign up: which roles may self-register, and are new users active immediately? | | Open |
| 14 | What is 24.dev (URL or package) for animations? No public library found under that name. | | Open |
| 15 | Demo seed users: email, password, and role for each of the three roles? | | Open |
