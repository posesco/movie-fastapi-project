import pytest
from fastapi import status
from src.core.config import settings

@pytest.mark.asyncio
async def test_register_user_success(client):
    # Try to register a new user
    user_data = {
        "name": "Test",
        "surname": "User",
        "username": "newtestuser",
        "email": "newtestuser@example.com",
        "password": "testpassword"
    }
    
    # The endpoint uses Form data
    response = await client.post(
        "/api/v1/user/register",
        data=user_data
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"success": "User created successfully"}

@pytest.mark.asyncio
async def test_register_user_duplicate_username(client):
    user_data = {
        "username": settings.admin_user,
        "email": "unique@example.com",
        "password": "testpassword"
    }
    response = await client.post("/api/v1/user/register", data=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["error"] == "Username already exists"
