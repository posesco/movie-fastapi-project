import pytest
from src.core.config import settings
from fastapi import status

@pytest.mark.asyncio
async def test_login_admin(client):
    response = await client.post(
        "/api/v1/user/login",
        data={"username": settings.admin_user, "password": settings.admin_pass},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
