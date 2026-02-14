from fastapi import FastAPI, HTTPException
from psycopg.errors import Error

from .config import DBHealthResponse, EmittersResponse, HealthResponse, VersionResponse, settings
from .db import check_db_connection, list_emitters

app = FastAPI(title="Methane Hotspot API", version=settings.app_version)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/version", response_model=VersionResponse)
def version() -> VersionResponse:
    return VersionResponse(version=settings.app_version)


@app.get("/db/health", response_model=DBHealthResponse)
def db_health() -> DBHealthResponse:
    connected, detail = check_db_connection()
    status = "ok" if connected else "error"
    return DBHealthResponse(status=status, detail=detail)


@app.get("/emitters", response_model=EmittersResponse)
def get_emitters() -> EmittersResponse:
    try:
        emitters = list_emitters()
    except Error as exc:
        raise HTTPException(status_code=503, detail=f"database unavailable: {exc}") from exc

    return EmittersResponse(emitters=emitters)
