"""
Test d'intégration pour l'endpoint /api/agent/respond
"""
import pytest
from fastapi.testclient import TestClient
from back.app import app
from uuid import UUID
import os

client = TestClient(app)

def test_agent_respond_integration(tmp_path):
    # Démarre une session via /api/scenarios/start avec le bon nom de scénario
    response = client.post("/api/scenarios/start", json={"scenario_name": "Les_Pierres_du_Passe.md", "character_id": "test-character"})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    session_id = data["session_id"]
    # Envoie un message à l'agent MJ
    message = "Bonjour, que vois-je autour de moi ?"
    response2 = client.post(f"/api/agent/respond?session_id={session_id}", json={"message": message})
    assert response2.status_code == 200
    data2 = response2.json()
    assert "response" in data2
    assert isinstance(data2["response"], str)
    # Vérifie la persistance mémoire (le fichier JSONL doit exister)
    memory_path = f"data/sessions/{session_id}.jsonl"
    assert os.path.exists(memory_path)
    with open(memory_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert any("Bonjour" in l for l in lines)
