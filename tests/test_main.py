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
    # Register a temporary test user
    register_response = client.post(
        "/auth/register",
        json={
            "username": "pytest_user",
            "email": "pytest_user@example.com",
            "password": "Test@12345",
            "role": "user",
            "patient_type": "New Patient",
            "age": 21,
            "gender": "Female",
            "disease": "None"
        }
    )

    # User may already exist from an earlier test run
    assert register_response.status_code in [200, 400]

    # Test login
    response = client.post(
        "/auth/login",
        json={
            "username": "pytest_user",
            "password": "Test@12345"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_doctors_endpoint_requires_authentication():
    response = client.get("/doctors")

    assert response.status_code in [401, 403]