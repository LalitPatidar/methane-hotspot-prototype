# Implementation Blueprint (Execution Loop)

This document is the **single source of truth** for incremental implementation work.

Use this loop for every coding turn:
1. Pick the next task with status `ready` (or the first `pending` task if none are ready).
2. Implement only that task (small vertical slice).
3. Add/update tests.
4. Update docs impacted by the task.
5. Mark task status and add a short progress note.

---

## Status legend
- `pending` — not started
- `ready` — approved to implement next
- `in_progress` — currently being implemented
- `blocked` — waiting on prerequisite/decision
- `done` — merged and verified

---

## Phase 1 — Real TROPOMI ingest adapter (Milestone 1)

### T1.1 Add source abstraction for ingest input
- **Status:** `done`
- **Goal:** Let ingest run from either fixture or real data source without breaking command interface.
- **Scope:**
  - Add `--source {fixture,real}` (default fixture for safety).
  - Keep existing artifact output contract unchanged (`raw/raw_refs.json`, `processed/observations.json`, `metadata.json`).
- **Acceptance checks:**
  - `make ingest` still works with fixture mode.
  - Existing ingest tests pass.
- **Progress notes:**
  - 2026-02-17: Added `--source {fixture,real}` ingest selection with fixture default, retained artifact contract, and added a guardrail error for unimplemented real source path plus tests.

### T1.2 Implement real TROPOMI fetch adapter (MVP path)
- **Status:** `ready`
- **Goal:** Fetch open TROPOMI observations by AOI/date and normalize to project observation schema.
- **Scope:**
  - Add adapter module under `pipelines/jobs/` (or `pipelines/sources/`).
  - Output normalized records with: `observation_id`, `observed_on`, `latitude`, `longitude`, `ch4_ppb`, `qa_value`.
  - Record dataset/product/version/source URL(s) in raw refs metadata.
- **Acceptance checks:**
  - Real-source mode writes deterministic artifacts for the same AOI/date run.
  - No secrets committed; credentials (if any) only via env vars.
- **Progress notes:**
  - None yet.

### T1.3 AOI parsing + validation
- **Status:** `pending`
- **Goal:** Support stable AOI definitions for reproducible ingest.
- **Scope:**
  - Support AOI as named preset and/or bbox (`min_lon,min_lat,max_lon,max_lat`).
  - Validate coordinate ranges and order.
- **Acceptance checks:**
  - Invalid AOI returns clear error.
  - Tests cover bbox parsing and validation failures.
- **Progress notes:**
  - None yet.

### T1.4 QA filtering hardening
- **Status:** `pending`
- **Goal:** Keep QA filtering configurable and explicit in metadata.
- **Scope:**
  - Ensure QA threshold is applied identically across fixture/real modes.
  - Persist QA threshold and pass/fail counts in metadata.
- **Acceptance checks:**
  - Tests verify counts and dropped IDs/records where available.
- **Progress notes:**
  - None yet.

### T1.5 Ingest observability + debug mode
- **Status:** `pending`
- **Goal:** Improve troubleshooting while keeping structured logs.
- **Scope:**
  - Add runtime stats (duration_ms, source_count, qa_pass_count).
  - Optional debug artifact dump controlled by env/config.
- **Acceptance checks:**
  - Job stdout remains JSON summary.
  - Metadata includes runtime + counts.
- **Progress notes:**
  - None yet.

---

## Phase 2 — Detection engine hardening (Milestone 2)

### T2.1 Robust baseline and anomaly scoring module
- **Status:** `pending`
- **Goal:** Move detection math into testable module with deterministic outputs.
- **Scope:**
  - Extract baseline/anomaly logic out of CLI script.
  - Keep default threshold env-driven.
- **Acceptance checks:**
  - Unit tests for baseline and anomaly edge cases.
- **Progress notes:**
  - None yet.

### T2.2 Polygon clustering output
- **Status:** `pending`
- **Goal:** Replace single-point candidate output with clustered hotspot polygons.
- **Scope:**
  - Cluster neighboring anomalies.
  - Emit polygon geometry + centroid + area.
- **Acceptance checks:**
  - Fixture test generates stable hotspot IDs/geometries.
- **Progress notes:**
  - None yet.

### T2.3 Detect metadata completeness
- **Status:** `pending`
- **Goal:** Ensure explainability/provenance fields are complete and documented.
- **Scope:**
  - Persist `anomaly_score`, `threshold`, `qa_pass_ratio`, `pixel_count`, `area_km2`.
  - Include ingest run linkage in metadata.
- **Acceptance checks:**
  - Existing detect tests expanded for all evidence fields.
- **Progress notes:**
  - None yet.

---

## Phase 3 — Publish to PostGIS + emitter tracking (Milestone 3)

### T3.1 Add detect-to-DB publish job
- **Status:** `pending`
- **Goal:** Upsert hotspot artifacts into PostGIS `hotspots` table.
- **Scope:**
  - New pipeline stage command (`make publish-hotspots` or equivalent).
  - Idempotent upsert by stable hotspot ID.
- **Acceptance checks:**
  - Re-running publish does not duplicate rows.
- **Progress notes:**
  - None yet.

### T3.2 Emitter tracking job
- **Status:** `pending`
- **Goal:** Link hotspots over time into stable emitters.
- **Scope:**
  - Spatiotemporal linking logic.
  - Deterministic emitter ID strategy and rolling stats.
- **Acceptance checks:**
  - Tests for overlap/split/reappearance.
- **Progress notes:**
  - None yet.

### T3.3 API evidence integration
- **Status:** `pending`
- **Goal:** Ensure API reads published hotspot and emitter evidence from DB.
- **Scope:**
  - Verify `/emitters`, `/emitters/{id}`, `/hotspots` align with DB-published artifacts.
- **Acceptance checks:**
  - Integration tests with seeded/published data.
- **Progress notes:**
  - None yet.

---

## Phase 4 — EMIT confirmation layer (Milestone 6)

### T4.1 EMIT ingest adapter
- **Status:** `pending`
- **Goal:** Ingest EMIT plume polygons and metadata from open source products.
- **Scope:**
  - Add EMIT fixture + real-source adapter path.
  - Preserve raw refs and processed artifacts.
- **Acceptance checks:**
  - Deterministic fixture tests for overlap/non-overlap cases.
- **Progress notes:**
  - None yet.

### T4.2 EMIT-to-emitter linking
- **Status:** `pending`
- **Goal:** Mark emitter confirmation state by spatial/time linkage.
- **Scope:**
  - Linking rules by intersection/distance + date window.
  - Write to `confirmations` and expose linkage status.
- **Acceptance checks:**
  - API and tests show confirmed vs unconfirmed emitters.
- **Progress notes:**
  - None yet.

### T4.3 Confirmation API endpoint
- **Status:** `pending`
- **Goal:** Implement planned confirmations API contract.
- **Scope:**
  - Add `GET /confirmations` with relevant filters.
  - Update `docs/api_contract.md`.
- **Acceptance checks:**
  - API tests for success + invalid filter + DB unavailable paths.
- **Progress notes:**
  - None yet.

---

## Phase 5 — Web MVP completion (Milestone 5)

### T5.1 Replace map placeholder with live map
- **Status:** `pending`
- **Goal:** Render hotspots + emitters on an interactive map.
- **Scope:**
  - Integrate map library and API-backed overlays.
- **Acceptance checks:**
  - Manual smoke screenshot + web tests updated.
- **Progress notes:**
  - None yet.

### T5.2 AOI/date controls and timeline flow
- **Status:** `pending`
- **Goal:** Allow users to query hotspots by date range and AOI.
- **Scope:**
  - Add controls and API query integration.
- **Acceptance checks:**
  - User can select AOI/date and see updated results.
- **Progress notes:**
  - None yet.

### T5.3 Emitter detail panel with evidence
- **Status:** `pending`
- **Goal:** Show emitter evidence timeline and conservative language.
- **Scope:**
  - Build detail panel using `/emitters/{id}` evidence fields.
- **Acceptance checks:**
  - UI shows anomaly/QA evidence and avoids overclaiming.
- **Progress notes:**
  - None yet.

---

## Operating rules for future turns
- Always update this file when finishing a task:
  - mark completed task as `done`;
  - set next task to `ready`;
  - append a dated progress note.
- If blocked, mark `blocked` and add exact unblock condition.
- Keep each implementation PR focused on **one task ID** from this blueprint.
