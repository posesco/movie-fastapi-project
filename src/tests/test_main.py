from fastapi.testclient import TestClient
from main import app
from fastapi import status

client = TestClient(app)


def test_redirect_to_status():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == "/_status/"


def test_redirect_to_status_follow():
    response = client.get("/", follow_redirects=True)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert data["status"] == "Live"


def test_health_check():
    response = client.get("/_status/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "db_status" in data
    assert "uptime" in data
    assert data["status"] == "Live"
    assert isinstance(data["uptime"], str)
