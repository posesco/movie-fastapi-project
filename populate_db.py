import json
import urllib.request
import urllib.parse
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configuration
BASE_URL = "http://localhost/api/v1"
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
    print(f"Starting population with user: {USERNAME}...")
    
    try:
        with open(MOVIES_FILE, "r", encoding="utf-8") as f:
            movies = json.load(f)
        print(f"Loaded {len(movies)} movies.")
    except Exception as e:
        print(f"Error reading {MOVIES_FILE}: {e}"); return

    # Login
    print("Obtaining token...")
    res, code = make_request(f"{BASE_URL}/user/login", data={"username": USERNAME, "password": PASSWORD}, is_form=True)
    
    if code != 200:
        print(f"Login error ({code}): {res.get('detail')}"); return
    
    headers = {"Authorization": f"Bearer {res.get('access_token')}"}
    
    # Upload in batches
    total = 0
    for i in range(0, len(movies), BATCH_SIZE):
        batch = movies[i:i + BATCH_SIZE]
        print(f"Uploading batch {i//BATCH_SIZE + 1}...")
        res, code = make_request(f"{BASE_URL}/movies/", data=batch, headers=headers)
        if code in [200, 201]:
            total += len(batch)
            print(f"OK. Total: {total}/{len(movies)}")
        else:
            print(f"Error ({code}): {res.get('detail')}"); break
            
    print(f"\nPopulation finished! Total uploaded: {total} movies.")

if __name__ == "__main__":
    populate()
