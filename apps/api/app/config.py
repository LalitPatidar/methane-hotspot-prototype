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
