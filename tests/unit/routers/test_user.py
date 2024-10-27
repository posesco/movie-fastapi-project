from fastapi.testclient import TestClient
from config.settings import settings
from fastapi import status
from main import app


client = TestClient(app)


def test_login_admin():
    response = client.post(
        "/login/",
        data={"username": settings.admin_user, "password": settings.admin_pass},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "success" in data
    assert isinstance(data["success"], str)


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}
