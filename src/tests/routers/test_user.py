from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_user():
    
    pass