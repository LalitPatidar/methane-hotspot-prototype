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
