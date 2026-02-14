import json
import os
from pathlib import Path

from psycopg import connect

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "pipelines" / "fixtures" / "sample_emitters.geojson"
MIGRATION_PATH = ROOT / "migrations" / "001_init.sql"


def main() -> None:
    database_url = os.getenv("DATABASE_URL", "postgresql://methane:methane@localhost:5432/methane")

    with connect(database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(MIGRATION_PATH.read_text())

            fixture = json.loads(FIXTURE_PATH.read_text())
            for feature in fixture["features"]:
                props = feature["properties"]
                geom = json.dumps(feature["geometry"])
                cur.execute(
                    """
                    INSERT INTO emitters (id, name, confidence, detection_count, last_seen, geom)
                    VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
                    ON CONFLICT (id) DO UPDATE SET
                      name = EXCLUDED.name,
                      confidence = EXCLUDED.confidence,
                      detection_count = EXCLUDED.detection_count,
                      last_seen = EXCLUDED.last_seen,
                      geom = EXCLUDED.geom
                    """,
                    (
                        props["id"],
                        props["name"],
                        props["confidence"],
                        props["detection_count"],
                        props["last_seen"],
                        geom,
                    ),
                )
        conn.commit()

    print(f"Seeded emitters from {FIXTURE_PATH}")


if __name__ == "__main__":
    main()
