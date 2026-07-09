import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key"  # noqa: S105

from fastapi import status
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/api/v1/health/")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["status"] == "healthy"
    assert body["version"] == "1.0.0"
    assert body["database"] == "connected"


def test_health_check_db_failure() -> None:
    """Simulate database failure by overriding ``get_db`` with a broken session."""

    from unittest.mock import MagicMock

    from sqlalchemy.orm import Session as SASession

    def broken_get_db():
        mock_session = MagicMock(spec=SASession)
        mock_session.execute.side_effect = Exception("DB connection lost")
        yield mock_session  # type: ignore[misc]

    app.dependency_overrides[get_db] = broken_get_db
    try:
        response = client.get("/api/v1/health/")
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        body = response.json()
        assert body["status"] == "unhealthy"
        assert body["database"] == "disconnected"
    finally:
        app.dependency_overrides.clear()
