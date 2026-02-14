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
