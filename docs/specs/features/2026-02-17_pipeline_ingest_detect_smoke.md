# Feature Spec: Milestone 0 ingest/detect smoke workflow

## Links
- Parent requirement(s): FR-1, FR-2, NFR-1
- Related issue: docs/next_issues.md (Issue 1 + Issue 2 bootstrap)

## Problem
The repository defines `make ingest` and `make detect` as required commands, but they are not implemented. This blocks reproducible pipeline validation in local development and CI.

## Scope
- In:
  - Add fixture-based ingest and detect jobs runnable without external services.
  - Add `make ingest` and `make detect` targets.
  - Add tests that validate command-path behavior for ingest/detect jobs.
  - Update docs to reflect smoke workflow and current project state.
- Out:
  - Real satellite API fetching.
  - Production hotspot clustering/tracking.

## Proposed design
- Data model changes:
  - None (filesystem artifact smoke outputs only).
- API changes:
  - None.
- Pipeline changes:
  - New ingest job reads fixture observations, applies configurable QA threshold, writes raw refs + processed observations + metadata.
  - New detect job reads ingest artifacts, computes robust baseline/threshold, and writes hotspot candidates with explainability fields.
- UI changes:
  - None.

## Acceptance criteria
1. `make ingest` succeeds and writes deterministic artifact + metadata output.
2. `make detect` succeeds after ingest and writes hotspot output with explainability fields.
3. Tests validate ingest filtering/provenance and detect evidence generation.
4. Documentation includes exact local smoke commands.

## Test plan
- Unit:
  - `pytest pipelines/tests/test_ingest_detect_jobs.py`
- Integration:
  - `make test` (includes pipeline tests).
- Manual smoke:
  - `make ingest`
  - `make detect`

## Rollout/ops
- Commands:
  - `make ingest`
  - `make detect`
- Backfill/migration:
  - None.
- Observability additions:
  - JSON summary logs from jobs (artifact paths + counts).

## Risks + mitigations
- Risk: Overfitting logic to fixture-only behavior.
  - Mitigation: Keep algorithm minimal and clearly marked as smoke baseline in docs.
