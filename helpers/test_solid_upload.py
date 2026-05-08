import asyncio
import httpx
from src.core.config import settings

async def verify_local_upload():
    # 1. Login
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        login_res = await client.post(
            "/api/v1/user/login",
            data={"username": settings.admin_user, "password": settings.admin_pass},
        )
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.text}")
            return
        
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Upload file
        files = {"file": ("test.png", b"fake image data", "image/png")}
        upload_res = await client.post("/api/v1/upload/", files=files, headers=headers)
        
        if upload_res.status_code == 201:
            print("Upload successful!")
            print(f"Response: {upload_res.json()}")
            url = upload_res.json()["url"]
            
            # 3. Check if file is accessible
            # Note: We use localhost:80 (Nginx) which should route to app
            # But the URL returned is /static/...
            static_res = await client.get(url)
            if static_res.status_code == 200:
                print("Static file accessible!")
            else:
                print(f"Static file NOT accessible: {static_res.status_code}")
        else:
            print(f"Upload failed: {upload_res.status_code} - {upload_res.text}")

if __name__ == "__main__":
    # Ensure STORAGE_BACKEND is set to local before running this if testing local
    asyncio.run(verify_local_upload())
