# Implementation Roadmap (Spec-Driven)

## Milestone 0 — Baseline hardening

### Goal
Stabilize scaffold so all expected developer commands and CI checks are aligned.

### Deliverables
- Add `make ingest` and `make detect` smoke targets.
- Add fixture-backed smoke tests for ingest/detect command paths.
- Document local runbook for repeatable MVP demos.

### Exit criteria
- All default commands run successfully on a fresh environment.
- CI validates lint + tests + command smoke checks.

---

## Milestone 1 — TROPOMI ingest + preprocess

### Goal
Implement deterministic ingestion with configurable QA and provenance capture.

### Deliverables
- AOI/date-range ingestion job.
- Preprocess job with QA threshold config.
- Raw/processed separation and metadata persistence.

### Exit criteria
- Re-running ingest for same parameters does not duplicate outputs.
- Metadata includes dataset/product/version/time/AOI/QA fields.

---

## Milestone 2 — Detection engine

### Goal
Produce daily hotspot candidates with explainability fields.

### Deliverables
- Background estimation + anomaly score.
- Thresholding + clustering into hotspot geometries.
- Persistence of anomaly/threshold/QA/pixel/area evidence.

### Exit criteria
- Fixture tests demonstrate deterministic hotspot output.
- Detection method doc reflects actual algorithm and thresholds.

---

## Milestone 3 — Emitter tracking

### Goal
Link repeated hotspot detections into persistent emitter candidates.

### Deliverables
- Spatiotemporal linking logic.
- Stable emitter ID strategy.
- Confidence/persistence scoring model.

### Exit criteria
- Unit tests cover overlap, split, and reappearance cases.
- Emitter detail API returns timeline evidence from tracked history.

---

## Milestone 4 — API expansion

### Goal
Serve complete MVP data retrieval and filtering workflows.

### Deliverables
- AOI + date-range hotspot retrieval.
- Confirmation endpoint(s) for EMIT overlays.
- Pagination/filtering where needed for scalability.

### Exit criteria
- API contract docs fully match implemented responses.
- Integration tests validate key UI query paths.

---

## Milestone 5 — Web MVP completion

### Goal
Deliver user-complete workflow in the web app.

### Deliverables
- Map integration (hotspots + emitters overlays).
- AOI selector and date/date-range controls.
- Emitter detail panel with time-series evidence.

### Exit criteria
- MVP user journey (1–6) is executable end-to-end.
- UI wording remains conservative: “candidate emitter / hotspot enhancement”.

---

## Milestone 6 — EMIT confirmation integration

### Goal
Enrich evidence quality with optional plume confirmations.

### Deliverables
- EMIT ingest and normalization pipeline.
- Spatial/time linking between EMIT plumes and emitters.
- UI confirmation overlay and API flags.

### Exit criteria
- Confirmed/non-confirmed emitters distinguishable in API/UI.
- Fixtures include overlap and non-overlap test cases.
