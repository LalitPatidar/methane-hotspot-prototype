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
