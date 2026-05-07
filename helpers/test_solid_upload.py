import asyncio
import httpx
import sys

async def test_upload():
    # URL de la API (asumiendo que corre en el puerto 80 según GEMINI.md)
    base_url = "http://localhost/api/v1"
    
    # 1. Obtener token (necesitamos un usuario)
    # Asumiendo credenciales por defecto del admin según GEMINI.md
    print("--- Obteniendo Token ---")
    async with httpx.AsyncClient() as client:
        try:
            login_res = await client.post(
                f"{base_url}/login/access-token",
                data={
                    "username": "admin@example.com",
                    "password": "admin"
                }
            )
            login_res.raise_for_status()
            token = login_res.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("Token obtenido con éxito.")
        except Exception as e:
            print(f"Error login: {e}")
            return

        # 2. Probar subida con contexto MOVIE_POSTER
        print("\n--- Probando Subida (Contexto: posters) ---")
        files = {"file": ("test_image.png", b"fake-image-content", "image/png")}
        try:
            upload_res = await client.post(
                f"{base_url}/upload/",
                params={"context": "posters"},
                files=files,
                headers=headers
            )
            upload_res.raise_for_status()
            data = upload_res.json()
            print("Respuesta Exitosa:")
            print(f"  URL: {data['url']}")
            print(f"  Path: {data['path']}")
            print(f"  Context: {data['context']}")
            
            if "posters/user_" in data["path"]:
                print("\n✅ VALIDACIÓN EXITOSA: La ruta sigue el patrón SOLID esperado.")
            else:
                print("\n❌ FALLO: La ruta no coincide con el patrón esperado.")
                
        except Exception as e:
            print(f"Error upload: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")

if __name__ == "__main__":
    asyncio.run(test_upload())
