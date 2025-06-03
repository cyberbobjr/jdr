from fastapi.testclient import TestClient
from back.app import app

def test_list_characters(client, isolated_data_dir):
    response = client.get("/api/characters")
    assert response.status_code == 200
    data = response.json()
    assert "characters" in data
    assert isinstance(data["characters"], list)
    assert len(data["characters"]) > 0
