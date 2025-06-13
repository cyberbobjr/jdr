import uuid
import os
from unittest.mock import patch, MagicMock


def test_get_scenario_history_returns_full_history(tmp_path, monkeypatch, client):
    """
    ### test_get_scenario_history_returns_full_history
    **Description:** Vérifie que l'endpoint /api/scenarios/history/{session_id} retourne bien l'historique complet des messages de la session.
    **Paramètres :**
    - `tmp_path` (Path) : Dossier temporaire pytest pour stocker les fichiers de session.
    - `monkeypatch` (pytest fixture) : Pour patcher les chemins d'accès aux dossiers de données.
    - `client` (TestClient) : Client FastAPI pour les tests d'API.
    **Retour :** None (assertions sur la réponse JSON).
    """
    session_id = str(uuid.uuid4())
    scenario_name = "TestScenario.md"
    character_id = str(uuid.uuid4())

    # Préparer le dossier scénario temporaire
    scenarios_dir = tmp_path / "scenarios"
    scenarios_dir.mkdir()
    (scenarios_dir / scenario_name).write_text("# Test\nContenu du scénario de test.", encoding="utf-8")

    # Créer les fichiers de session pour simuler une session existante
    sessions_dir = tmp_path / "sessions" / session_id
    sessions_dir.mkdir(parents=True)
    (sessions_dir / "character.txt").write_text(character_id, encoding="utf-8")
    (sessions_dir / "scenario.txt").write_text(scenario_name, encoding="utf-8")

    # Patch le chemin de base pour pointer sur le dossier temporaire
    import back.services.scenario_service as scenario_service
    base_dir = tmp_path
    monkeypatch.setattr(scenario_service.os.path, "abspath", lambda path: str(base_dir) if "data" in path else path)
    monkeypatch.setattr(scenario_service.os.path, "join", os.path.join)
    monkeypatch.setattr(scenario_service.os.path, "exists", os.path.exists)
    monkeypatch.setattr(scenario_service.os, "makedirs", os.makedirs)

    # Mock de l'agent et du store pour retourner un historique simulé
    mock_agent = MagicMock()
    mock_message1 = MagicMock()
    mock_message1.model_dump.return_value = {"role": "user", "text": "Bonjour"}
    mock_message2 = MagicMock()
    mock_message2.model_dump.return_value = {"role": "assistant", "text": "Bienvenue !"}
    mock_message3 = MagicMock()
    mock_message3.model_dump.return_value = {"role": "tool", "text": "Résultat d'outil"}
    mock_store = MagicMock()
    # Prépare un historique JSON natif simulé (format attendu par l'API)
    fake_history = [
        {"parts": [{"content": "Bonjour", "timestamp": "2025-01-01T00:00:00Z", "part_kind": "user-prompt"}], "role": "user"},
        {"parts": [{"content": "Bienvenue !", "timestamp": "2025-01-01T00:00:01Z", "part_kind": "text"}], "role": "assistant"},
        {"parts": [{"content": "Résultat d'outil", "timestamp": "2025-01-01T00:00:02Z", "part_kind": "tool-return"}], "role": "tool"}
    ]
    mock_store.read_json_history.return_value = fake_history
    # Patch aussi la classe PydanticJsonlStore pour forcer l'utilisation du mock partout
    # Patch get_session_info pour retourner aussi character_id (attendu par la route)
    fake_session_info = {"scenario_name": scenario_name, "character_id": character_id}
    with patch('back.routers.scenarios.build_gm_agent_pydantic', return_value=(mock_agent, mock_store)), \
         patch('back.routers.scenarios.ScenarioService.get_session_info', return_value=fake_session_info), \
         patch('back.agents.gm_agent_pydantic.PydanticJsonlStore', return_value=mock_store):
        response = client.get(f"/api/scenarios/history/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert "history" in data
        assert isinstance(data["history"], list)
        assert len(data["history"]) == 3
        assert data["history"][0]["role"] == "user"
        assert data["history"][1]["role"] == "assistant"
        assert data["history"][2]["role"] == "tool"


def test_get_scenario_history_404_if_session_not_found(client):
    """
    ### test_get_scenario_history_404_if_session_not_found
    **Description:** Vérifie que l'endpoint /api/scenarios/history/{session_id} retourne une 404 si la session n'existe pas.
    **Paramètres :**
    - `client` (TestClient) : Client FastAPI pour les tests d'API.
    **Retour :** None (assertion sur le code de statut HTTP).
    """
    import uuid
    session_id = str(uuid.uuid4())
    with patch('back.routers.scenarios.ScenarioService.get_session_info', side_effect=FileNotFoundError("not found")):
        response = client.get(f"/api/scenarios/history/{session_id}")
        assert response.status_code == 404
        assert "detail" in response.json()
