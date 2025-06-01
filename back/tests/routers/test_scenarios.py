import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    from back.app import app
    return TestClient(app)

def test_start_scenario(client):
    response = client.post("/api/scenarios/start", json={
        "scenario_name": "Les_Pierres_du_Passe.md",
        "character_id": "79e55c14-7dd5-4189-b209-ea88f6d067eb"
    })
    assert response.status_code == 200
    assert "démarré avec succès" in response.json()["message"]

def test_start_scenario_returns_session_id(tmp_path, monkeypatch, client):
    """
    ### test_start_scenario_returns_session_id
    **Description:** Vérifie que l'endpoint /api/scenarios/start retourne bien un id de session, le nom du scénario et l'id du personnage.
    **Paramètres :**
    - `tmp_path` (Path) : Dossier temporaire pytest pour stocker les fichiers de session.
    - `monkeypatch` (pytest fixture) : Pour patcher les chemins d'accès aux dossiers de données.
    - `client` (TestClient) : Client FastAPI pour les tests d'API.
    **Retour :** None (assertions sur la réponse JSON).
    """
    import uuid
    import os
    scenario_name = "TestScenario.md"
    character_id = str(uuid.uuid4())
    # Préparer le dossier scénario temporaire
    scenarios_dir = tmp_path / "scenarios"
    scenarios_dir.mkdir()
    (scenarios_dir / scenario_name).write_text("# Test\nContenu.", encoding="utf-8")
    # Patch le chemin de base pour pointer sur le dossier temporaire
    import back.services.scenario_service as scenario_service
    base_dir = tmp_path
    monkeypatch.setattr(scenario_service.os.path, "abspath", lambda path: str(base_dir) if "data" in path else path)
    monkeypatch.setattr(scenario_service.os.path, "join", os.path.join)
    monkeypatch.setattr(scenario_service.os.path, "exists", os.path.exists)
    monkeypatch.setattr(scenario_service.os, "makedirs", os.makedirs)
    # Appel API
    response = client.post("/api/scenarios/start", json={"scenario_name": scenario_name, "character_id": character_id})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["scenario_name"] == scenario_name
    assert data["character_id"] == character_id
    assert data["message"].startswith("Scénario")
def test_agent_respond_returns_llm_response(tmp_path, monkeypatch, client):
    """
    ### test_agent_respond_returns_llm_response
    **Description:** Vérifie que l'endpoint /api/agent/respond retourne bien une réponse du LLM et persiste l'historique.
    **Paramètres :**
    - `tmp_path` (Path) : Dossier temporaire pytest pour stocker les fichiers de session.
    - `monkeypatch` (pytest fixture) : Pour patcher les chemins d'accès aux dossiers de données.
    - `client` (TestClient) : Client FastAPI pour les tests d'API.
    **Retour :** None (assertions sur la réponse JSON).
    """
    import uuid
    import os
    from back.agents.gm_agent import JsonlChatMessageStore
    # Préparer une session et un historique minimal
    session_id = str(uuid.uuid4())
    session_file = tmp_path / f"{session_id}.jsonl"
    store = JsonlChatMessageStore(str(session_file))
    store.save([])  # Historique vide
    # Patch le chemin de base pour pointer sur le dossier temporaire
    import back.agents.gm_agent as gm_agent_mod
    monkeypatch.setattr(gm_agent_mod, "JsonlChatMessageStore", lambda path: JsonlChatMessageStore(str(session_file)))
    # Appel API (correction : message dans le body JSON)
    response = client.post(f"/api/agent/respond?session_id={session_id}", json={"message": "bonjour"})
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    # Vérifie que l'historique a bien été persisté
    messages = store.load()
    assert any("bonjour" in m.text.lower() for m in messages)
