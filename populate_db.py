import json
import urllib.request
import urllib.parse
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración
BASE_URL = "http://localhost:8000/api/v1"
MOVIES_FILE = "movies.json"
BATCH_SIZE = 10
USERNAME = os.getenv("ADMIN_USER", "admin")
PASSWORD = os.getenv("ADMIN_PASS", "admin")

def make_request(url, data=None, headers=None, method="POST", is_form=False):
    if headers is None: headers = {}
    payload = None
    if data:
        if is_form:
            payload = urllib.parse.urlencode(data).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            payload = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"
    
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8")), response.getcode()
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8")), e.code
        except:
            return {"detail": f"HTTP Error {e.code}"}, e.code
    except Exception as e:
        return {"detail": str(e)}, 500

def populate():
    print(f"Iniciando población con usuario: {USERNAME}...")
    
    try:
        with open(MOVIES_FILE, "r", encoding="utf-8") as f:
            movies = json.load(f)
        print(f"Cargadas {len(movies)} películas.")
    except Exception as e:
        print(f"Error al leer {MOVIES_FILE}: {e}"); return

    # Login
    print("Obteniendo token...")
    res, code = make_request(f"{BASE_URL}/user/login", data={"username": USERNAME, "password": PASSWORD}, is_form=True)
    
    if code != 200:
        print(f"Error en login ({code}): {res.get('detail')}"); return
    
    headers = {"Authorization": f"Bearer {res.get('access_token')}"}
    
    # Subir en bloques
    total = 0
    for i in range(0, len(movies), BATCH_SIZE):
        batch = movies[i:i + BATCH_SIZE]
        print(f"Subiendo bloque {i//BATCH_SIZE + 1}...")
        res, code = make_request(f"{BASE_URL}/movies/", data=batch, headers=headers)
        if code in [200, 201]:
            total += len(batch)
            print(f"OK. Total: {total}/{len(movies)}")
        else:
            print(f"Error ({code}): {res.get('detail')}"); break
            
    print(f"\n¡Población finalizada! Total subido: {total} películas.")

if __name__ == "__main__":
    populate()
