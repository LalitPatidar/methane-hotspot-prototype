from datetime import date

from psycopg import connect
from psycopg.errors import Error

from .config import settings


def check_db_connection() -> tuple[bool, str]:
    try:
        with connect(settings.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True, "connected"
    except Error as exc:
        return False, str(exc)


def list_emitters() -> list[dict[str, object]]:
    with connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    name,
                    confidence,
                    detection_count,
                    last_seen::text,
                    ST_Y(geom) AS latitude,
                    ST_X(geom) AS longitude
                FROM emitters
                ORDER BY confidence DESC, id ASC
                """
            )
            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "confidence": float(row[2]),
            "detection_count": row[3],
            "last_seen": row[4],
            "latitude": float(row[5]),
            "longitude": float(row[6]),
        }
        for row in rows
    ]


def get_emitter_with_evidence(emitter_id: str) -> dict[str, object] | None:
    with connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    name,
                    confidence,
                    detection_count,
                    last_seen::text,
                    ST_Y(geom) AS latitude,
                    ST_X(geom) AS longitude
                FROM emitters
                WHERE id = %s
                """,
                (emitter_id,),
            )
            emitter_row = cur.fetchone()

            if emitter_row is None:
                return None

            cur.execute(
                """
                SELECT
                    id,
                    observed_on::text,
                    anomaly_score,
                    area_km2,
                    pixel_count,
                    qa_pass_ratio
                FROM hotspots
                WHERE emitter_id = %s
                ORDER BY observed_on DESC, id ASC
                """,
                (emitter_id,),
            )
            hotspot_rows = cur.fetchall()

    return {
        "id": emitter_row[0],
        "name": emitter_row[1],
        "confidence": float(emitter_row[2]),
        "detection_count": emitter_row[3],
        "last_seen": emitter_row[4],
        "latitude": float(emitter_row[5]),
        "longitude": float(emitter_row[6]),
        "hotspot_evidence": [
            {
                "hotspot_id": row[0],
                "observed_on": row[1],
                "anomaly_score": float(row[2]),
                "area_km2": float(row[3]),
                "pixel_count": row[4],
                "qa_pass_ratio": float(row[5]),
            }
            for row in hotspot_rows
        ],
    }


def list_hotspots_by_date(observed_on: date) -> list[dict[str, object]]:
    with connect(settings.database_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    emitter_id,
                    observed_on::text,
                    anomaly_score,
                    area_km2,
                    pixel_count,
                    qa_pass_ratio,
                    ST_Y(ST_Centroid(geom)) AS centroid_latitude,
                    ST_X(ST_Centroid(geom)) AS centroid_longitude
                FROM hotspots
                WHERE observed_on = %s
                ORDER BY anomaly_score DESC, id ASC
                """,
                (observed_on,),
            )
            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "emitter_id": row[1],
            "observed_on": row[2],
            "anomaly_score": float(row[3]),
            "area_km2": float(row[4]),
            "pixel_count": row[5],
            "qa_pass_ratio": float(row[6]),
            "centroid_latitude": float(row[7]),
            "centroid_longitude": float(row[8]),
        }
        for row in rows
    ]
