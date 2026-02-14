# Next Issues (create on GitHub)

## 1) TROPOMI ingest (AOI + date range)
- [ ] Add pipeline job to ingest TROPOMI by AOI/date range
- [ ] Add configurable QA filter and metadata capture
- [ ] Store raw references + processed artifact pointers
- [ ] Add tests with fixtures

## 2) Anomaly + hotspot polygons
- [ ] Implement background estimation + anomaly scoring
- [ ] Threshold and cluster anomalies into polygons
- [ ] Persist hotspot evidence fields
- [ ] Document method updates

## 3) Persistence tracking (emitters)
- [ ] Build spatiotemporal linking for hotspot sequences
- [ ] Maintain stable emitter IDs and rolling stats
- [ ] Add confidence scoring function
- [ ] Add unit/integration tests

## 4) EMIT ingest + emitter linking
- [ ] Ingest EMIT plume polygons + metadata
- [ ] Link plume events to emitters by spatial rules
- [ ] Mark confirmation state in API responses
- [ ] Add test fixtures for overlap/non-overlap

## 5) UI overlays + time slider
- [ ] Add map overlay for daily hotspots
- [ ] Add persistent emitter markers and filter controls
- [ ] Add daily date picker/time slider
- [ ] Add emitter detail panel with evidence timeline
