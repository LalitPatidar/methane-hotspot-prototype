CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS emitters (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  confidence NUMERIC NOT NULL,
  detection_count INTEGER NOT NULL DEFAULT 0,
  last_seen DATE NOT NULL,
  geom GEOMETRY(Point, 4326) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS hotspots (
  id TEXT PRIMARY KEY,
  emitter_id TEXT REFERENCES emitters(id),
  observed_on DATE NOT NULL,
  anomaly_score NUMERIC NOT NULL,
  area_km2 NUMERIC NOT NULL,
  pixel_count INTEGER NOT NULL,
  qa_pass_ratio NUMERIC NOT NULL,
  geom GEOMETRY(Polygon, 4326) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS confirmations (
  id TEXT PRIMARY KEY,
  emitter_id TEXT REFERENCES emitters(id),
  source TEXT NOT NULL,
  observed_on DATE NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  geom GEOMETRY(Polygon, 4326) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_emitters_last_seen ON emitters(last_seen);
CREATE INDEX IF NOT EXISTS idx_hotspots_observed_on ON hotspots(observed_on);
CREATE INDEX IF NOT EXISTS idx_hotspots_geom ON hotspots USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_confirmations_geom ON confirmations USING GIST (geom);
