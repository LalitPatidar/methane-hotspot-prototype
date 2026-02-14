# Architecture (MVP)

## Components
- **apps/api (FastAPI)**: serves health/version and methane hotspot/emitter APIs.
- **apps/web (Next.js)**: map dashboard and emitter detail UX.
- **Postgres + PostGIS**: stores emitters, hotspots, confirmations.
- **pipelines/jobs**: local scripts for ingest, detect, track, publish.

## Data flow
1. Ingest open satellite datasets (TROPOMI always-on, EMIT optional confirmation).
2. Preprocess + QA filter + anomaly detection.
3. Persist hotspot polygons and evidence stats in PostGIS.
4. Track persistent emitters from repeated detections.
5. Expose via API and visualize in web map.

## Deployment path
- MVP: local filesystem artifacts + local PostGIS.
- Later: object storage, task scheduler/orchestrator, tiled map publishing.
