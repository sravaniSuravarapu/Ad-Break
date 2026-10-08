# Tech Stack
Project: adbreak-manager (Ad Break & Campaign Booking Manager)

## Backend (backend/)
- Python 3.12
- FastAPI + Pydantic v2
- SQLAlchemy 2.0 + Alembic
- PostgreSQL (row-level locking for BR-10)
- JWT auth (python-jose or PyJWT) with role dependencies
- pytest + httpx
- uv or pip + ruff
- Architecture: routers -> services -> models; business rules only in services/

## Frontend (frontend/)
- React 18 + Vite + TypeScript
- Tailwind CSS
- TanStack Query, React Router
- Recharts for dashboards
- React Hook Form + Zod
- Vitest + React Testing Library
- Uses only endpoints in the backend OpenAPI schema

## Local setup
- Docker Compose (Postgres + API)
