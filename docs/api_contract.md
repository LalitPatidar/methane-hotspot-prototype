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

## Planned endpoints
- `GET /emitters` — list persistent emitters with confidence/rank.
- `GET /hotspots?date=YYYY-MM-DD` — hotspot polygons by day.
- `GET /emitters/{id}` — emitter details and evidence timeline.
