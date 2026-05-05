import json
import urllib.request
import urllib.parse
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configuration
VERSION_API = "v1"
BASE_URL = f"http://localhost/api/{VERSION_API}"
MOVIES_FILE = "helpers/movies.json"
USERS_FILE = "helpers/users.json"
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
    
    # Upload movies individually
    total_movies = 0
    for movie in movies:
        title = movie.get('title')
        print(f"Uploading movie: {title}...")
        res, code = make_request(f"{BASE_URL}/movies/", data=movie, headers=headers)
        
        if code in [200, 201]:
            total_movies += 1
        elif code == 409 or (code == 500 and res.get('type') == 'IntegrityError'):
            print(f"Información: La película '{title}' ya existe.")
        else:
            msg = res.get('message') or res.get('error') or res.get('detail')
            print(f"Error ({code}): {msg}")
    
    # Upload users individually
    total_users = 0
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
        print(f"Loaded {len(users)} users from {USERS_FILE}.")
    except Exception as e:
        print(f"Error reading {USERS_FILE}: {e}")
        users = []

    for user in users:
        username = user.get('username')
        print(f"Uploading user: {username}...")
        # Register is public, but we can send headers anyway
        res, code = make_request(f"{BASE_URL}/user/register", data=user, headers=headers)
        
        if code in [200, 201]:
            total_users += 1
        elif code == 409:
            print(f"Información: El usuario '{username}' ya existe.")
        else:
            msg = res.get('message') or res.get('error') or res.get('detail')
            print(f"Error ({code}): {msg}")

    print(f"\nPopulation finished! Total uploaded: {total_movies} movies and {total_users} users.")

if __name__ == "__main__":
    populate()
