# Detection Method (MVP)

## Layer A: TROPOMI always-on scan
1. QA filter (config-driven threshold).
2. Regrid to analysis grid.
3. Local robust background estimate.
4. Enhancement = observed - background.
5. Robust anomaly score.
6. Threshold + clustering -> hotspot polygons.
7. Store evidence (`anomaly_score`, `area`, `pixel_count`, `qa_pass_ratio`).

## Persistence tracking
- Aggregate repeated hotspot detections across days.
- Maintain stable emitter IDs with detection counters and confidence proxy.

## Layer B: EMIT confirmation
- Ingest plume polygons and metadata.
- Link to emitters by intersection/distance.
- Mark emitter as confirmed when linked at least once.


## Current smoke implementation
- `make ingest` uses a local TROPOMI-like fixture and applies configurable QA filtering (`INGEST_QA_THRESHOLD`, default `0.85`).
- Raw references and processed observations are written separately with stage metadata for provenance.
- `make detect` computes a median CH4 background on ingested observations, then flags hotspots when `anomaly_score = observed - background` exceeds `DETECT_ANOMALY_THRESHOLD_PPB` (default `40`).
- Each candidate stores explainability fields (`anomaly_score`, `threshold`, `qa_pass_ratio`, `pixel_count`, `area_km2`, centroid).
