import pytest
from fastapi import status
from src.core.config import settings

@pytest.mark.asyncio
async def test_update_user_self_success(client):
    # 1. Register a normal user
    username = "selfuser"
    user_data = {
        "name": "Self",
        "surname": "User",
        "username": username,
        "email": "self@example.com",
        "password": "testpassword"
    }
    await client.post("/api/v1/user/register", data=user_data)

    # 2. Login as that user
    login_data = {"username": username, "password": "testpassword"}
    login_res = await client.post("/api/v1/user/login", data=login_data)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Update self
    update_data = {"name": "UpdatedName"}
    response = await client.put(f"/api/v1/user/{username}", json=update_data, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "UpdatedName"

@pytest.mark.asyncio
async def test_update_other_user_as_user_forbidden(client):
    # 1. Register user A
    await client.post("/api/v1/user/register", data={
        "name": "User", "surname": "A", "username": "usera",
        "email": "usera@example.com", "password": "password"
    })

    # 2. Register user B
    await client.post("/api/v1/user/register", data={
        "name": "User", "surname": "B", "username": "userb",
        "email": "userb@example.com", "password": "password"
    })

    # 3. Login as User A
    login_res = await client.post("/api/v1/user/login", data={"username": "usera", "password": "password"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Try to update User B
    response = await client.put("/api/v1/user/userb", json={"name": "Hacked"}, headers=headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["error"] == "You can only edit your own profile"

@pytest.mark.asyncio
async def test_update_user_as_admin_success(client):
    # 1. Login as super_admin to create an admin
    admin_login = await client.post("/api/v1/user/login", data={"username": settings.admin_user, "password": settings.admin_pass})
    sa_token = admin_login.json()["access_token"]
    sa_headers = {"Authorization": f"Bearer {sa_token}"}

    # Create user to become admin
    await client.post("/api/v1/user/register", data={
        "name": "Admin", "surname": "User", "username": "adminuser",
        "email": "admin@test.com", "password": "password"
    })
    
    # Assign admin role
    await client.put("/api/v1/user/assign-roles", json={"username": "adminuser", "roles": ["admin"]}, headers=sa_headers)

    # 2. Create a normal target user
    await client.post("/api/v1/user/register", data={
        "name": "Target", "surname": "User", "username": "targetuser",
        "email": "target@test.com", "password": "password"
    })

    # 3. Login as admin
    login_res = await client.post("/api/v1/user/login", data={"username": "adminuser", "password": "password"})
    admin_token = login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 4. Update target user as admin
    response = await client.put("/api/v1/user/targetuser", json={"name": "AdminUpdated"}, headers=admin_headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "AdminUpdated"

@pytest.mark.asyncio
async def test_admin_cannot_update_super_admin(client):
    # 1. Setup admin user
    admin_login = await client.post("/api/v1/user/login", data={"username": settings.admin_user, "password": settings.admin_pass})
    sa_token = admin_login.json()["access_token"]
    sa_headers = {"Authorization": f"Bearer {sa_token}"}

    await client.post("/api/v1/user/register", data={
        "name": "Admin", "surname": "X", "username": "adminx",
        "email": "adminx@test.com", "password": "password"
    })
    await client.put("/api/v1/user/assign-roles", json={"username": "adminx", "roles": ["admin"]}, headers=sa_headers)

    # 2. Login as admin
    login_res = await client.post("/api/v1/user/login", data={"username": "adminx", "password": "password"})
    admin_token = login_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Try to update super_admin
    response = await client.put(f"/api/v1/user/{settings.admin_user}", json={"name": "HackedSA"}, headers=admin_headers)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["error"] == "Admins cannot edit super_admin users"

@pytest.mark.asyncio
async def test_super_admin_can_update_anyone(client):
    # 1. Login as super_admin
    login_res = await client.post("/api/v1/user/login", data={"username": settings.admin_user, "password": settings.admin_pass})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Register some user
    await client.post("/api/v1/user/register", data={
        "name": "Any", "surname": "Body", "username": "anybody",
        "email": "anybody@test.com", "password": "password"
    })

    # 3. Update as super_admin
    response = await client.put("/api/v1/user/anybody", json={"surname": "SuperUpdated"}, headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["surname"] == "SuperUpdated"
