# Data Sources

## Sentinel-5P / TROPOMI CH4
- Purpose: daily coarse-resolution hotspot candidate generation.
- Access: open/public datasets.
- MVP use: anomaly-based hotspot extraction + persistence signals.

## NASA EMIT Methane Plumes
- Purpose: high-resolution confirmation events where coverage overlaps candidates.
- Access: open/public products.
- MVP use: confirmation overlay and emitter evidence enrichment.

## Notes
- QA filtering is mandatory and configurable.
- Preserve traceability metadata for dataset/product/time/AOI/thresholds.


### TROPOMI ingest adapter configuration (MVP)
- `INGEST_SOURCE=fixture|real` chooses deterministic fixture mode or open-source URL fetch mode.
- `INGEST_REAL_SOURCE_URL` points to an open JSON endpoint (or `file://` URL for deterministic local tests).
- Real-source payload is normalized to project observations with required fields: `observation_id`, `observed_on`, `latitude`, `longitude`, `ch4_ppb`, `qa_value`.
- Ingest artifacts store `source_urls` in `raw/raw_refs.json` and `metadata.json` for provenance.


## Google Earth Engine S5P L3 CH4 (MVP fast path)
- Dataset: `COPERNICUS/S5P/OFFL/L3_CH4`.
- Fetch stage: `pipelines/jobs/fetch_gee_ch4.py` filters by date + AOI, applies configurable QA mask (`qa_value >= GEE_QA_THRESHOLD`), and samples to points at configurable `GEE_SCALE_METERS`.
- Output artifacts: `pipelines/artifacts/source/gee/<run_id>/points.parquet` + `metadata.json`.
- Ingest stage: `pipelines/jobs/ingest_gee_ch4.py` converts Parquet points to `observations.json` shape used by `detect_hotspots.py`.
- Provenance: metadata captures dataset id, date range, AOI, thresholds, sampling scale, and point counts.
