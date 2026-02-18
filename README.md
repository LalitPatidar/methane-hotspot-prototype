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
6. (Optional) run real Google Earth Engine CH4 fetch + ingest + detect:
   ```bash
   make fetch_gee aoi=permian start=2026-02-01 end=2026-02-07
   make ingest_gee aoi=permian start=2026-02-01 end=2026-02-07
   make detect aoi=permian start=2026-02-01 end=2026-02-07
   ```
7. Run tests and lint:
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
- `make ingest` writes raw + processed artifacts under `pipelines/artifacts/ingest/<run_id>/` (default `--source fixture`). For real-source runs, set `INGEST_SOURCE=real` and `INGEST_REAL_SOURCE_URL=<open-endpoint-or-file-url>`.
- `make detect` reads the latest ingest run and writes hotspot evidence under `pipelines/artifacts/detect/<run_id>/`.
- Tune thresholds with env vars (for example `INGEST_QA_THRESHOLD=0.9 DETECT_ANOMALY_THRESHOLD_PPB=60 make detect`).

## Google Earth Engine authentication (for real CH4 fetch)

Dataset used for MVP real ingest: `COPERNICUS/S5P/OFFL/L3_CH4`.

### Local developer auth (interactive)
1. Install dependencies with `make setup`.
2. Authenticate once with:
   ```bash
   earthengine authenticate
   ```
3. Set `.env` values as needed (`GEE_PROJECT`, `GEE_AUTH_MODE=user`).

### Service account auth (CI/server)
1. Create/download a Google service account JSON key with Earth Engine access.
2. Set:
   - `GEE_AUTH_MODE=service_account`
   - `GEE_SERVICE_ACCOUNT_EMAIL=<service-account-email>`
   - `GEE_SERVICE_ACCOUNT_KEY_FILE=<path-to-json-key>`
   - Optional: `GEE_PROJECT=<gcp-project-id>`

### Runtime knobs
- `GEE_QA_THRESHOLD` (default `0.5`)
- `GEE_SCALE_METERS` (default `10000`)
- `GEE_MAX_POINTS` (default `50000`)
- `GEE_TILE_SCALE` (default `4`)
