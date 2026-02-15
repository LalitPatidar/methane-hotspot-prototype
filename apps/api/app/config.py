from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_version: str = "0.1.0"
    database_url: str = "postgresql://methane:methane@localhost:5432/methane"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()


class VersionResponse(BaseModel):
    version: str


class HealthResponse(BaseModel):
    status: str


class DBHealthResponse(BaseModel):
    status: str
    detail: str


class EmitterSummary(BaseModel):
    id: str
    name: str
    confidence: float
    detection_count: int
    last_seen: str
    latitude: float
    longitude: float


class EmittersResponse(BaseModel):
    emitters: list[EmitterSummary]


class HotspotEvidence(BaseModel):
    hotspot_id: str
    observed_on: str
    anomaly_score: float
    area_km2: float
    pixel_count: int
    qa_pass_ratio: float


class EmitterDetail(EmitterSummary):
    hotspot_evidence: list[HotspotEvidence]


class HotspotSummary(BaseModel):
    id: str
    emitter_id: str | None
    observed_on: str
    anomaly_score: float
    area_km2: float
    pixel_count: int
    qa_pass_ratio: float
    centroid_latitude: float
    centroid_longitude: float


class EmitterDetailResponse(BaseModel):
    emitter: EmitterDetail


class HotspotsResponse(BaseModel):
    hotspots: list[HotspotSummary]
