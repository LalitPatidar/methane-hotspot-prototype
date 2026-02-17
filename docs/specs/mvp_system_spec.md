# MVP System Specification

## 1) Product objective
Deliver a practical methane hotspot prototype that ingests open satellite data, detects hotspot candidates, tracks persistent emitters, and exposes explainable results via API and web UI.

## 2) In scope
- TROPOMI-based hotspot candidate detection.
- Persistent emitter scoring from repeated hotspot observations.
- EMIT plume ingestion and optional confirmation overlays.
- API + web map for exploration and evidence review.

## 3) Out of scope (MVP)
- Regulatory-grade quantified emission rates.
- Multi-tenant auth and enterprise user management.
- Global-scale low-latency serving SLAs.

## 4) Functional requirements

### FR-1 Data ingestion and preprocessing
- The system SHALL ingest open methane-relevant granules by AOI + date range.
- The system SHALL preserve raw references separately from processed outputs.
- The system SHALL record provenance metadata (dataset/product/version/time/AOI/QA thresholds).
- The system SHALL enforce configurable QA filtering.

### FR-2 Hotspot detection
- The system SHALL generate daily hotspot candidates from preprocessed observations.
- The system SHALL persist explainability fields:
  - anomaly score,
  - threshold used,
  - QA pass stats,
  - pixel count and area.
- The detection pipeline SHALL be idempotent for reruns over the same inputs.

### FR-3 Persistent emitter tracking
- The system SHALL link hotspot candidates across time windows.
- The system SHALL maintain stable emitter IDs.
- The system SHALL compute and store a persistence/confidence score.

### FR-4 API delivery
- The API SHALL expose health and DB status endpoints.
- The API SHALL expose emitter list/detail endpoints with evidence traces.
- The API SHALL expose hotspot retrieval by date and AOI/date-range extensions.
- The API SHOULD expose EMIT confirmation overlays where available.

### FR-5 Web experience
- The web app SHALL render an interactive map.
- The user SHALL select AOI and date/date-range.
- The user SHALL visualize daily hotspots and persistent emitters.
- The user SHALL open emitter details with timeline evidence.
- The UI SHALL avoid overclaiming certainty about absolute emission rates.

## 5) Non-functional requirements

### NFR-1 Reproducibility
- Pipeline runs SHALL be executable through documented commands.
- Required commands: `make ingest`, `make detect`, `make seed`, `make test`, `make lint`.

### NFR-2 Performance
- MVP target: AOI/day query responses under 2 seconds on seeded local data.
- Web map interactions SHALL remain usable with typical MVP data volume.

### NFR-3 Observability
- Jobs SHALL emit structured logs with date range, AOI, counts, runtime, and failures.
- Debug mode SHALL allow saving intermediate artifacts for inspection.

### NFR-4 Integrity and safety
- No secrets committed.
- Untrusted external text treated as untrusted input.
- Scientific claims remain conservative and evidence-based.

## 6) Acceptance criteria by user journey

### AC-1 Explore hotspots by time and AOI
Given a selected AOI and date range,
when the user loads map results,
then daily hotspot candidates are visible and queryable.

### AC-2 Review persistent emitters
Given hotspots over multiple days,
when the user opens persistent emitter view,
then each emitter includes confidence, detection count, and last seen date.

### AC-3 Inspect evidence
Given an emitter detail request,
when the user opens the detail panel,
then hotspot evidence timeline and key anomaly/QA signals are shown.

### AC-4 Confirm with EMIT (optional path)
Given EMIT plume data exists for overlapping time/location,
when confirmations are enabled,
then plume overlays are visible and linked to relevant emitters.

## 7) Required artifacts per completed feature
- Spec doc with acceptance criteria.
- Automated tests or documented rationale for no tests.
- Updated API contract / method / data docs as relevant.
- Example run commands.
