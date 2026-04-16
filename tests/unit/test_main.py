import pytest
from fastapi import status

@pytest.mark.asyncio
async def test_redirect_to_status(client):
    response = await client.get("/", follow_redirects=False)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers["location"] == "/_status/"

@pytest.mark.asyncio
async def test_redirect_to_status_follow(client):
    response = await client.get("/", follow_redirects=True)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert data["status"] == "Live"

@pytest.mark.asyncio
async def test_health_status(client):
    response = await client.get("/_status/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "Live"
    assert "db_status" in data
