import os
import json
import urllib.request
import urllib.parse
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Configuration
API_VERSION = "v1"
BASE_URL = f"http://localhost/api/{API_VERSION}"
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin")
NUM_USERS = 10
NUM_MOVIES = 20

# External APIs Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "") # Get yours at https://www.themoviedb.org/settings/api
RANDOM_USER_URL = "https://randomuser.me/api/"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

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

def get_auth_token():
    print("Authenticating with local API...")
    res, code = make_request(
        f"{BASE_URL}/user/login", 
        data={"username": ADMIN_USER, "password": ADMIN_PASS}, 
        is_form=True
    )
    if code == 200:
        return res.get("access_token")
    print(f" Login failed: {res}")
    return None

def upload_from_url(external_url, token, folder=None):
    if not external_url:
        return None
    try:
        # Download
        response = requests.get(external_url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to download image from {external_url}")
            return external_url
        
        # Determine filename
        filename = os.path.basename(urllib.parse.urlparse(external_url).path)
        if not filename or "." not in filename:
            filename = f"upload_{int(time.time())}.jpg"
            
        # Upload using the internal endpoint
        upload_url = f"{BASE_URL}/upload/"
        params = {"folder": folder} if folder else {}
        files = {"file": (filename, response.content, response.headers.get('Content-Type', 'image/jpeg'))}
        headers = {"Authorization": f"Bearer {token}"}
        
        up_res = requests.post(upload_url, params=params, files=files, headers=headers, timeout=20)
        if up_res.status_code == 201:
            new_url = up_res.json().get("url")
            return new_url
        else:
            print(f"Failed to upload image: {up_res.text}")
            return external_url
    except Exception as e:
        print(f"Error in upload_from_url: {e}")
        return external_url

def fetch_external_users(count=10):
    print(f"Fetching {count} random users from RandomUser.me...")
    url = f"{RANDOM_USER_URL}?results={count}&nat=us,es,gb"
    res, code = make_request(url, method="GET")
    if code != 200:
        print(" Error fetching users")
        return []
    
    users = []
    for u in res.get("results", []):
        street = u["location"]["street"]
        address = f"{street['number']} {street['name']}, {u['location']['city']}, {u['location']['country']}"
        users.append({
            "name": u["name"]["first"],
            "surname": u["name"]["last"],
            "username": u["login"]["username"],
            "email": u["email"],
            "password": "Password123!", # Standardized for LAB
            "phone": u["phone"],
            "address": address,
            "picture": u["picture"]["large"]
        })
    return users

def fetch_external_movies(count=NUM_MOVIES):
    if not TMDB_API_KEY:
        print("TMDB_API_KEY not found in .env. Skipping movie fetching.")
        return []

    print(f"Fetching {count} trending movies from TMDB...")
    trending_url = f"{TMDB_BASE_URL}/trending/movie/day?api_key={TMDB_API_KEY}"
    res, code = make_request(trending_url, method="GET")
    if code != 200:
        print(f" Error fetching trending movies: {res}")
        return []

    movies_data = []
    for m in res.get("results", [])[:count]:
        # Get details for extra info (director, studio, box_office)
        movie_id = m["id"]
        details_url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits"
        details, d_code = make_request(details_url, method="GET")
        
        if d_code == 200:
            # Find director
            director = "Unknown"
            for crew in details.get("credits", {}).get("crew", []):
                if crew["job"] == "Director":
                    director = crew["name"]
                    break
            
            # Map to our Movie schema
            movies_data.append({
                "title": details["title"],
                "overview": details["overview"][:350], # Truncate to fit schema
                "year": int(details["release_date"][:4]) if details.get("release_date") else 2024,
                "rating": details["vote_average"],
                "category": details["genres"][0]["name"] if details.get("genres") else "Drama",
                "director": director[:30],
                "studio": details["production_companies"][0]["name"][:60] if details.get("production_companies") else "Independent",
                "box_office": details.get("revenue", 0),
                "image_url": f"https://image.tmdb.org/t/p/w500{details['poster_path']}" if details.get("poster_path") else None
            })
            time.sleep(0.5) # Be nice to API
            
    return movies_data

def smart_populate():
    token = get_auth_token()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Populate Users
    users = fetch_external_users(NUM_USERS)
    time.sleep(0.5)
    for user in users:
        print(f"Processing user: {user['username']}...")
        if user.get("picture"):
            user["picture"] = upload_from_url(user["picture"], token, folder="profiles")
        
        print(f"Registering: {user['username']}...")
        res, code = make_request(f"{BASE_URL}/user/register", data=user)
        if code in [200, 201]:
            print(f"User {user['username']} created.")
        else:
            print(f"{user['username']}: {res.get('detail', 'Already exists')}")

    # Populate Movies
    movies = fetch_external_movies(NUM_MOVIES)
    time.sleep(0.5)
    for movie in movies:
        print(f"Processing movie: {movie['title']}...")
        if movie.get("image_url"):
            movie["image_url"] = upload_from_url(movie["image_url"], token, folder="movies")

        print(f"Uploading: {movie['title']}...")
        res, code = make_request(f"{BASE_URL}/movies/", data=movie, headers=headers)
        if code in [200, 201]:
            print(f"Movie {movie['title']} uploaded.")
        else:
            print(f"{movie['title']}: {res.get('detail', 'Error or exists')}")

    print("\n Smart Population complete!")

if __name__ == "__main__":
    smart_populate()

