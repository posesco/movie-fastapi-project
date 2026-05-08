import pytest
from fastapi import status
from src.core.config import settings

@pytest.mark.asyncio
async def test_register_extra_params_fails(client):
    user_data = {
        "name": "Extra",
        "surname": "Param",
        "username": "extrauser",
        "email": "extra@example.com",
        "password": "password123",
        "extra_field": "should_fail"
    }
    response = await client.post("/api/v1/user/register", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    # Custom response uses "message" for validation errors
    assert "extra_field" in str(response.json()["message"])

@pytest.mark.asyncio
async def test_update_user_extra_params_fails(client):
    # 1. Login
    login_data = {"username": settings.admin_user, "password": settings.admin_pass}
    login_res = await client.post("/api/v1/user/login", data=login_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Update with extra field
    update_data = {
        "name": "Updated",
        "unknown_field": "hacker"
    }
    response = await client.put(f"/api/v1/user/{settings.admin_user}", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "unknown_field" in str(response.json()["message"])
