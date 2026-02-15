from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


def test_no_auth_when_key_empty(client):
    """Endpoints accessible when api_key is empty (dev mode)."""
    assert settings.api_key == ""
    resp = client.post("/api/v1/users", json={"username": "alice"})
    assert resp.status_code == 201


def test_403_when_key_configured_but_missing(db):
    """Returns 403 when api_key is set but request has no header."""

    def _override():
        yield db

    from app.core.database import get_db

    app.dependency_overrides[get_db] = _override

    with patch.object(settings, "api_key", "test-secret"):
        with TestClient(app) as c:
            resp = c.post("/api/v1/users", json={"username": "alice"})
            assert resp.status_code == 403

    app.dependency_overrides.clear()


def test_403_when_key_configured_but_wrong(db):
    """Returns 403 when api_key is set but request sends wrong key."""

    def _override():
        yield db

    from app.core.database import get_db

    app.dependency_overrides[get_db] = _override

    with patch.object(settings, "api_key", "test-secret"):
        with TestClient(app) as c:
            resp = c.post(
                "/api/v1/users",
                json={"username": "alice"},
                headers={"X-API-Key": "wrong-key"},
            )
            assert resp.status_code == 403

    app.dependency_overrides.clear()


def test_200_when_key_matches(db):
    """Returns 200 when correct API key is provided."""

    def _override():
        yield db

    from app.core.database import get_db

    app.dependency_overrides[get_db] = _override

    with patch.object(settings, "api_key", "test-secret"):
        with TestClient(app) as c:
            resp = c.post(
                "/api/v1/users",
                json={"username": "alice"},
                headers={"X-API-Key": "test-secret"},
            )
            assert resp.status_code == 201

    app.dependency_overrides.clear()


def test_security_headers(client):
    """Response includes security headers."""
    resp = client.post("/api/v1/users", json={"username": "bob"})
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
