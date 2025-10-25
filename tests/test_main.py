from fastapi.testclient import TestClient
from src.server.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "MCP Server is running"}
