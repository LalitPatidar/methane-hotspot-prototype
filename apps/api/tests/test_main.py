from fastapi.testclient import TestClient
from psycopg import OperationalError

from app.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version() -> None:
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()


def test_emitters(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.main.list_emitters",
        lambda: [
            {
                "id": "em-001",
                "name": "Permian Candidate 1",
                "confidence": 0.88,
                "detection_count": 6,
                "last_seen": "2026-02-12",
                "latitude": 31.731,
                "longitude": -102.117,
            }
        ],
    )

    response = client.get("/emitters")

    assert response.status_code == 200
    assert response.json() == {
        "emitters": [
            {
                "id": "em-001",
                "name": "Permian Candidate 1",
                "confidence": 0.88,
                "detection_count": 6,
                "last_seen": "2026-02-12",
                "latitude": 31.731,
                "longitude": -102.117,
            }
        ]
    }


def test_emitters_returns_503_when_db_unavailable(monkeypatch) -> None:
    def _raise() -> list[dict[str, object]]:
        raise OperationalError("db down")

    monkeypatch.setattr("app.main.list_emitters", _raise)

    response = client.get("/emitters")

    assert response.status_code == 503
    assert "database unavailable" in response.json()["detail"]


def test_emitter_detail(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.main.get_emitter_with_evidence",
        lambda emitter_id: {
            "id": emitter_id,
            "name": "Permian Candidate 1",
            "confidence": 0.88,
            "detection_count": 12,
            "last_seen": "2026-02-12",
            "latitude": 31.731,
            "longitude": -102.117,
            "hotspot_evidence": [
                {
                    "hotspot_id": "hs-1001",
                    "observed_on": "2026-02-12",
                    "anomaly_score": 2.4,
                    "area_km2": 1.2,
                    "pixel_count": 43,
                    "qa_pass_ratio": 0.95,
                }
            ],
        },
    )

    response = client.get("/emitters/em-001")

    assert response.status_code == 200
    body = response.json()
    assert body["emitter"]["id"] == "em-001"
    assert body["emitter"]["hotspot_evidence"][0]["hotspot_id"] == "hs-1001"


def test_emitter_detail_returns_404(monkeypatch) -> None:
    monkeypatch.setattr("app.main.get_emitter_with_evidence", lambda _emitter_id: None)

    response = client.get("/emitters/em-missing")

    assert response.status_code == 404
    assert "emitter not found" in response.json()["detail"]


def test_emitter_detail_returns_503_when_db_unavailable(monkeypatch) -> None:
    def _raise(_emitter_id: str) -> dict[str, object] | None:
        raise OperationalError("db down")

    monkeypatch.setattr("app.main.get_emitter_with_evidence", _raise)

    response = client.get("/emitters/em-001")

    assert response.status_code == 503
    assert "database unavailable" in response.json()["detail"]


def test_hotspots_by_date(monkeypatch) -> None:
    monkeypatch.setattr(
        "app.main.list_hotspots_by_date",
        lambda _observed_on: [
            {
                "id": "hs-1001",
                "emitter_id": "em-001",
                "observed_on": "2026-02-12",
                "anomaly_score": 2.4,
                "area_km2": 1.2,
                "pixel_count": 43,
                "qa_pass_ratio": 0.95,
                "centroid_latitude": 31.731,
                "centroid_longitude": -102.117,
            }
        ],
    )

    response = client.get("/hotspots?date=2026-02-12")

    assert response.status_code == 200
    assert response.json()["hotspots"][0]["id"] == "hs-1001"


def test_hotspots_returns_422_for_invalid_date() -> None:
    response = client.get("/hotspots?date=2026/02/12")

    assert response.status_code == 422


def test_hotspots_returns_503_when_db_unavailable(monkeypatch) -> None:
    def _raise(_observed_on):
        raise OperationalError("db down")

    monkeypatch.setattr("app.main.list_hotspots_by_date", _raise)

    response = client.get("/hotspots?date=2026-02-12")

    assert response.status_code == 503
    assert "database unavailable" in response.json()["detail"]
