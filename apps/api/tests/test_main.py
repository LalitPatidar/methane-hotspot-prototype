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
