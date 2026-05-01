from fastapi.testclient import TestClient
from src.core.config import settings
from fastapi import status
from src.main import app


client = TestClient(app)


def test_login_admin():
    response = client.post(
        "/api/v1/user/login",
        data={"username": settings.admin_user, "password": settings.admin_pass},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}
