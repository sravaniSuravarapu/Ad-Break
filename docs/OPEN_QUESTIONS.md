| # | Question | Answer | Status |
|---|----------|--------|--------|
| 1 | Confirm rate card per daypart values for demo seed data. | Price per 10 seconds, different per daypart, stored on the rate card and not hardcoded in booking logic. Demo seed: morning 8000, daytime 6000, prime 15000, late_night 5000 (INR). | Answered |
| 2 | Category conflict rule: exact category match only? | Yes. Exact category string match. No fuzzy or partial match. | Answered |
| 3 | Can a booking be moved to another break (or cancel + rebook)? | Cancel, rebook, and move. Move/rebook re-runs all validations. The original booking keeps its history. | Answered |
| 4 | Is Agency an entity for MVP? | Yes. Agency is a table, related to advertisers and campaigns. | Answered |
| 5 | Timestamps: created_at and updated_at (UTC) on every table? | Yes. Both on every table, stored in UTC. UI converts for display. | Answered |
| 6 | created_by and changed_by: non-null UUID foreign keys to users.id? | Yes where a user performs the action. Nullable only when no user context exists (self sign-up). Never insert a fake user id. | Answered |
| 7 | booking_status_history.old_status nullable? | Yes. First row has old_status null. | Answered |
| 8 | Unique on rate_card.daypart, channels.name, advertisers.name? | Yes. | Answered |
| 9 | Enum values confirmed? | Roles, dayparts, campaign statuses, and booking statuses as listed in the MVP decisions. | Answered |
| 10 | Add uvicorn? | Yes. | Answered |
| 11 | Compose defaults? | Postgres 16, database/user/password adbreak, host port 5432, API port 8000, all via environment variables. | Answered |
| 12 | Figma Dev link? | https://www.figma.com/design/sr4S9rtLh9bystfh8XuYKt/Free-Crypto-Dashboard---RecehTok-Dark--Community-?node-id=11-0&m=dev | Answered |
| 13 | Sign up roles and activation? | All three roles may self-register and are active immediately. Authorization still enforced after login. | Answered |
| 14 | Animation library? | 21st.dev (not 24.dev). Components are copied into the app theme, not imported as a runtime package. | Answered |
| 15 | Demo users? | sales@example.com, traffic@example.com, revenue@example.com, password Demo@12345, one per role. Dev only. | Answered |
