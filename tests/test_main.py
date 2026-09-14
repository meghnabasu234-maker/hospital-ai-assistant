import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/docs")
    assert response.status_code == 200


def test_login_endpoint_exists():
    response = client.post(
        "/auth/login",
        json={
            "username": "newpatient01",
            "password": "Test@12345"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_doctors_endpoint_requires_authentication():
    response = client.get("/doctors")

    assert response.status_code in [401, 403]