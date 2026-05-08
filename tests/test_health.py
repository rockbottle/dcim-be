import os
import pytest

def test_liveness_probe(client):
    """
    Checks the /health/healthz endpoint.
    Verifies the app is alive and correctly reading environment variables.
    """
    # Mocking environment variables for the test context
    os.environ["MY_POD_NAME"] = "test-pod-123"
    
    response = client.get("/health/healthz")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["pod_name"] == "test-pod-123"

def test_readiness_probe_success(client):
    """
    Checks the /health/readyz endpoint.
    Verifies that the database connection (SQLite in this case) is active.
    """
    response = client.get("/health/readyz")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert "Database is connected" in response.json()["message"]

def test_readiness_probe_failure(client, monkeypatch):
    """
    Optional: Simulates a database failure to ensure it returns a 503.
    """
    from sqlalchemy.orm import Session
    
    def mock_execute(*args, **kwargs):
        raise Exception("Connection Timeout")

    # We patch the session execute to simulate a crash
    monkeypatch.setattr(Session, "execute", mock_execute)
    
    response = client.get("/health/readyz")
    assert response.status_code == 503
    assert "Database connection failed" in response.json()["detail"]