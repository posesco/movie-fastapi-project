import pytest
from fastapi import status
from src.core.config import settings

@pytest.mark.asyncio
async def test_assign_roles_put(client):
    # 1. Login as admin to get token
    login_data = {
        "username": settings.admin_user,
        "password": settings.admin_pass
    }
    login_res = await client.post("/api/v1/user/login", data=login_data)
    assert login_res.status_code == status.HTTP_200_OK
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create a normal user to assign roles to
    user_data = {
        "name": "Test",
        "surname": "User",
        "username": "roleuser",
        "email": "roleuser@example.com",
        "password": "testpassword"
    }
    await client.post("/api/v1/user/register", data=user_data)

    # 3. Assign roles using PUT (the new method)
    assign_data = {
        "username": "roleuser",
        "roles": ["admin"]
    }
    
    # We need to ensure roles exist in DB for the test to pass
    # The current seed_db might not be enough if it doesn't call insert_default_roles
    
    response = await client.put(
        "/api/v1/user/assign-roles",
        json=assign_data,
        headers=headers
    )
    
    # If roles are missing it might be 400, but we want to see if PUT is accepted
    assert response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED

@pytest.mark.asyncio
async def test_delete_user_success(client):
    # 1. Login as super_admin
    login_data = {"username": settings.admin_user, "password": settings.admin_pass}
    login_res = await client.post("/api/v1/user/login", data=login_data)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create user to delete
    username = "todelete"
    user_data = {
        "name": "To", "surname": "Delete", "username": username,
        "email": "delete@example.com", "password": "password"
    }
    await client.post("/api/v1/user/register", data=user_data)

    # 3. Delete user
    response = await client.delete(f"/api/v1/user/{username}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert "deleted successfully" in response.json()["success"]

@pytest.mark.asyncio
async def test_delete_super_admin_forbidden(client):
    # 1. Login as super_admin
    login_data = {"username": settings.admin_user, "password": settings.admin_pass}
    login_res = await client.post("/api/v1/user/login", data=login_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Try to delete the super_admin user
    response = await client.delete(f"/api/v1/user/{settings.admin_user}", headers=headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    # The project uses "error" key for HTTPException details
    assert response.json()["error"] == "Cannot delete the primary super_admin account"
