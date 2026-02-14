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

## Planned endpoints
- `GET /hotspots?date=YYYY-MM-DD` — hotspot polygons by day.
- `GET /emitters/{id}` — emitter details and evidence timeline.
