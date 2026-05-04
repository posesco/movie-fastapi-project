import pytest
from fastapi import status
from src.core.config import settings

@pytest.mark.asyncio
async def test_read_users_me_no_password(client):
    # 1. Login as super_admin
    login_res = await client.post(
        "/api/v1/user/login", 
        data={"username": settings.admin_user, "password": settings.admin_pass}
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get /me
    response = await client.get("/api/v1/user/me", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # 3. Verify sensitive fields are NOT present
    assert "password" not in data
    assert "hashed_password" not in data
    
    # 4. Verify expected fields are present
    assert "username" in data
    assert data["username"] == settings.admin_user
    assert "roles" in data
    assert isinstance(data["roles"], list)
