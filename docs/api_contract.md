# API Contract (Initial)

## `GET /health`
Response:
```json
{"status": "ok"}
```

## `GET /version`
Response:
```json
{"version": "0.1.0"}
```

## `GET /db/health`
Response:
```json
{"status": "ok|error", "detail": "..."}
```

## `GET /emitters`
Returns persistent emitter candidates from PostGIS, ordered by confidence descending.

Success response (`200`):
```json
{
  "emitters": [
    {
      "id": "em-001",
      "name": "Permian Candidate 1",
      "confidence": 0.88,
      "detection_count": 6,
      "last_seen": "2026-02-12",
      "latitude": 31.731,
      "longitude": -102.117
    }
  ]
}
```

Unavailable database response (`503`):
```json
{"detail": "database unavailable: ..."}
```

## `GET /emitters/{id}`
Returns a single emitter with hotspot evidence used for persistence tracking explainability.

Success response (`200`):
```json
{
  "emitter": {
    "id": "em-001",
    "name": "Permian Candidate 1",
    "confidence": 0.88,
    "detection_count": 12,
    "last_seen": "2026-02-12",
    "latitude": 31.731,
    "longitude": -102.117,
    "hotspot_evidence": [
      {
        "hotspot_id": "hs-1001",
        "observed_on": "2026-02-12",
        "anomaly_score": 2.4,
        "area_km2": 1.2,
        "pixel_count": 43,
        "qa_pass_ratio": 0.95
      }
    ]
  }
}
```

Not found response (`404`):
```json
{"detail": "emitter not found: em-001"}
```

Unavailable database response (`503`):
```json
{"detail": "database unavailable: ..."}
```

## `GET /hotspots?date=YYYY-MM-DD`
Returns hotspot candidates for the requested day, ordered by anomaly score descending.

Success response (`200`):
```json
{
  "hotspots": [
    {
      "id": "hs-1001",
      "emitter_id": "em-001",
      "observed_on": "2026-02-12",
      "anomaly_score": 2.4,
      "area_km2": 1.2,
      "pixel_count": 43,
      "qa_pass_ratio": 0.95,
      "centroid_latitude": 31.731,
      "centroid_longitude": -102.117
    }
  ]
}
```

Validation response (`422`) for an invalid date format.

Unavailable database response (`503`):
```json
{"detail": "database unavailable: ..."}
```

## Planned endpoints
- `GET /confirmations?source=EMIT` — EMIT plume polygons and metadata.
