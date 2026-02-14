# Methane Hotspot Detection Prototype

Monorepo scaffold for an MVP that ingests open methane datasets, detects hotspot candidates, tracks persistent emitters, and serves results via API + web UI.

## Quickstart

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies:
   ```bash
   make setup
   ```
3. Start local stack (PostGIS + API + web):
   ```bash
   make dev
   ```
4. Seed sample data fixture:
   ```bash
   make seed
   ```
5. Run tests and lint:
   ```bash
   make test
   make lint
   ```

## Services
- API: http://localhost:8000 (`/health`, `/version`, `/db/health`)
- Web: http://localhost:3000
- PostGIS: localhost:5432

## Repo layout
- `apps/api` — FastAPI service
- `apps/web` — Next.js app
- `packages/core` — shared logic placeholder
- `pipelines/jobs` — ingest/detect/seed jobs
- `pipelines/fixtures` — sample data fixtures
- `migrations` — SQL schema migrations
- `docs` — architecture, API contract, methods, data sources
