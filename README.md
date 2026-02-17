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
5. Run pipeline smoke stages:
   ```bash
   make ingest
   make detect
   ```
6. Run tests and lint:
   ```bash
   make test
   make lint
   ```

## Services
- API: http://localhost:8000 (`/health`, `/version`, `/db/health`, `/emitters`)
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

## Specs-driven development
- Use `docs/specs/README.md` as the entrypoint for requirements, roadmap, and delivery workflow.
- Create feature specs under `docs/specs/features/` before implementation work.

## Pipeline smoke runbook
- `make ingest` writes raw + processed artifacts under `pipelines/artifacts/ingest/<run_id>/` (default `--source fixture`; use `INGEST_SOURCE=real` when the real adapter is implemented).
- `make detect` reads the latest ingest run and writes hotspot evidence under `pipelines/artifacts/detect/<run_id>/`.
- Tune thresholds with env vars (for example `INGEST_QA_THRESHOLD=0.9 DETECT_ANOMALY_THRESHOLD_PPB=60 make detect`).
