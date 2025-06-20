"""
Tests d'intégration pour le workflow de création de personnage via l'API creation.
"""
from fastapi.testclient import TestClient
from back.app import app

client = TestClient(app)

class TestCharacterCreationAPI:
    def test_create_new_character(self):
        response = client.post("/api/creation/new")
        assert response.status_code == 200
        data = response.json()
        assert "character_id" in data
        assert "created_at" in data
        assert data["status"] == "en_cours"
        self.character_id = data["character_id"]

    def test_save_and_status(self):
        # Création
        response = client.post("/api/creation/new")
        data = response.json()
        character_id = data["character_id"]
        # Sauvegarde
        character = {
            "id": character_id,
            "name": "TestHero",
            "race": "Nain",
            
            "created_at": data["created_at"],
            "status": "en_cours"
        }
        save_resp = client.post("/api/creation/save", json={"character_id": character_id, "character": character})
        assert save_resp.status_code == 200
        # Statut
        status_resp = client.get(f"/api/creation/status/{character_id}")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert status_data["character_id"] == character_id
        assert status_data["status"] == "en_cours"
