# Current State Analysis (as of 2026-02)

## 1) What exists today

### API (`apps/api`)
- FastAPI app with basic operational endpoints:
  - `GET /health`
  - `GET /version`
  - `GET /db/health`
- Initial domain endpoints:
  - `GET /emitters`
  - `GET /emitters/{id}`
  - `GET /hotspots?date=YYYY-MM-DD`
- Tests validate success and DB-unavailable behavior for the implemented endpoints.

### Web (`apps/web`)
- Next.js app shell with a map placeholder.
- Mock emitter list component/data.
- Basic test scaffold in place.

### Data + storage
- Postgres/PostGIS migration scaffold (`migrations/001_init.sql`).
- Seed script and sample fixture data (`pipelines/jobs/seed_sample_data.py`, `pipelines/fixtures/sample_emitters.geojson`).

### Docs + operations
- Project docs for architecture, API contract, detection method, and data sources.
- Core developer commands available:
  - `make setup`, `make dev`, `make test`, `make lint`, `make seed`.

## 2) Gaps vs MVP success criteria

The AGENTS mission defines MVP success as:
1. Open web map.
2. Select date range + AOI.
3. View hotspots for each day.
4. View persistent emitters with score.
5. View emitter time series + evidence.
6. Optionally view EMIT-confirmed plume polygons.

### Gap summary

#### A. Pipeline is not yet end-to-end
- Missing production ingest stages for TROPOMI and EMIT.
- Missing preprocess + QA-filter implementation with configurable thresholds.
- Missing automated detect/track jobs and metadata lineage persistence.

#### B. API is scaffolded but not complete
- Endpoint set is partial vs full contract for operational analytics.
- No explicit AOI/date-range query APIs for hotspot timeline retrieval.
- Confirmation endpoints (EMIT plume data) still planned only.

#### C. Web experience is placeholder-level
- No map engine integration yet.
- No AOI/date controls or timeline browsing.
- No emitter detail panel with evidence charts/time series.

#### D. Operational maturity gaps
- `make ingest` and `make detect` are expected by repository rules but not yet implemented.
- No explicit scheduler/invocation strategy documented for repeatable runs.
- Limited observability and debug artifact retention strategy.

## 3) Highest-priority delivery objectives

1. Implement deterministic ingest/preprocess/detect/track pipeline stages with artifact + metadata outputs.
2. Expand API for timeline, AOI filtering, and confirmation overlays.
3. Replace UI placeholders with interactive map + controls + emitter evidence drill-down.
4. Add missing standard commands and CI checks for ingest/detect smoke workflows.
5. Strengthen scientific traceability (QA thresholds, anomaly evidence, provenance fields).

## 4) Risks to manage

- **Data volume/performance risk:** large raster ingestion could overwhelm local runs without chunking/caching.
- **False positives risk:** weak QA filtering can create unstable emitter tracking.
- **Contract drift risk:** UI and API may diverge without strict contract-first development.
- **Reproducibility risk:** pipeline reruns must remain idempotent and traceable.

## 5) Recommendation

Adopt a strict specs-driven delivery loop:
1. Write a feature spec with acceptance criteria and test plan.
2. Implement minimal slice.
3. Validate with deterministic fixtures.
4. Update docs/contracts together.
5. Merge only when criteria are demonstrably satisfied.
