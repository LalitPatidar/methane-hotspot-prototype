from datetime import date

from fastapi import FastAPI, HTTPException, Query
from psycopg.errors import Error

from .config import (
    DBHealthResponse,
    EmitterDetailResponse,
    EmittersResponse,
    HealthResponse,
    HotspotsResponse,
    VersionResponse,
    settings,
)
from .db import check_db_connection, get_emitter_with_evidence, list_emitters, list_hotspots_by_date

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


@app.get("/emitters/{emitter_id}", response_model=EmitterDetailResponse)
def get_emitter(emitter_id: str) -> EmitterDetailResponse:
    try:
        emitter = get_emitter_with_evidence(emitter_id)
    except Error as exc:
        raise HTTPException(status_code=503, detail=f"database unavailable: {exc}") from exc

    if emitter is None:
        raise HTTPException(status_code=404, detail=f"emitter not found: {emitter_id}")

    return EmitterDetailResponse(emitter=emitter)


@app.get("/hotspots", response_model=HotspotsResponse)
def get_hotspots(observed_on: date = Query(alias="date")) -> HotspotsResponse:
    try:
        hotspots = list_hotspots_by_date(observed_on)
    except Error as exc:
        raise HTTPException(status_code=503, detail=f"database unavailable: {exc}") from exc

    return HotspotsResponse(hotspots=hotspots)
