from fastapi import FastAPI

from .config import DBHealthResponse, HealthResponse, VersionResponse, settings
from .db import check_db_connection

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
