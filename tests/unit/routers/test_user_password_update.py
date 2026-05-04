import pytest
from fastapi import status
from src.core.config import settings

@pytest.mark.asyncio
async def test_update_password_self_with_confirmation_success(client):
    # 1. Register and login
    username = "passuser"
    password = "oldpassword"
    await client.post("/api/v1/user/register", data={
        "username": username, "email": "pass@test.com", "password": password,
        "name": "Pass", "surname": "User"
    })
    
    login_res = await client.post("/api/v1/user/login", data={"username": username, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Update password with current_password
    new_password = "newpassword"
    update_data = {
        "password": new_password,
        "current_password": password
    }
    response = await client.put(f"/api/v1/user/{username}", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    
    # 3. Verify new password works
    login_res = await client.post("/api/v1/user/login", data={"username": username, "password": new_password})
    assert login_res.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_update_password_self_no_confirmation_failure(client):
    # 1. Register and login
    username = "nopassuser"
    password = "oldpassword"
    await client.post("/api/v1/user/register", data={
        "username": username, "email": "nopass@test.com", "password": password,
        "name": "No", "surname": "Pass"
    })
    
    login_res = await client.post("/api/v1/user/login", data={"username": username, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Update password WITHOUT current_password
    update_data = {"password": "newpassword"}
    response = await client.put(f"/api/v1/user/{username}", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Current password is required" in response.json()["error"]

@pytest.mark.asyncio
async def test_update_password_self_wrong_confirmation_failure(client):
    # 1. Register and login
    username = "wrongpassuser"
    password = "oldpassword"
    await client.post("/api/v1/user/register", data={
        "username": username, "email": "wrongpass@test.com", "password": password,
        "name": "Wrong", "surname": "Pass"
    })
    
    login_res = await client.post("/api/v1/user/login", data={"username": username, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Update password with WRONG current_password
    update_data = {
        "password": "newpassword",
        "current_password": "nottheoldpassword"
    }
    response = await client.put(f"/api/v1/user/{username}", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid current password" in response.json()["error"]

@pytest.mark.asyncio
async def test_update_password_as_admin_no_confirmation_success(client):
    # 1. Login as super_admin
    sa_login = await client.post("/api/v1/user/login", data={"username": settings.admin_user, "password": settings.admin_pass})
    sa_token = sa_login.json()["access_token"]
    sa_headers = {"Authorization": f"Bearer {sa_token}"}

    # 2. Create target user
    target_username = "targetpass"
    target_password = "targetpassword"
    await client.post("/api/v1/user/register", data={
        "username": target_username, "email": "targetpass@test.com", "password": target_password,
        "name": "Target", "surname": "Pass"
    })

    # 3. Update target's password as super_admin WITHOUT current_password
    new_password = "adminchangedthis"
    update_data = {"password": new_password}
    response = await client.put(f"/api/v1/user/{target_username}", json=update_data, headers=sa_headers)
    
    assert response.status_code == status.HTTP_200_OK

    # 4. Verify new password works
    login_res = await client.post("/api/v1/user/login", data={"username": target_username, "password": new_password})
    assert login_res.status_code == status.HTTP_200_OK
