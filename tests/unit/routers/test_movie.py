import pytest
from fastapi import status
from src.core.config import settings

@pytest.mark.asyncio
async def test_get_movies_empty(client):
    response = await client.get("/api/v1/movies/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_movie_and_get_categories(client):
    # 1. Login as super_admin
    login_res = await client.post(
        "/api/v1/user/login",
        data={"username": settings.admin_user, "password": settings.admin_pass},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create a movie
    movie_data = {
        "title": "Inception",
        "overview": "A thief who steals corporate secrets through the use of dream-sharing technology.",
        "year": 2010,
        "rating": 8.8,
        "category": "Sci-Fi",
        "director": "Christopher Nolan",
        "studio": "Warner Bros.",
        "box_office": 836800000
    }
    response = await client.post("/api/v1/movies/", json=movie_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert "Inception" in response.json()["success"]

    # 3. Get categories
    response = await client.get("/api/v1/movies/categories")
    assert response.status_code == status.HTTP_200_OK
    assert "Sci-Fi" in response.json()

    # 4. Get by category
    response = await client.get("/api/v1/movies/category/?category=Sci-Fi")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Inception"
