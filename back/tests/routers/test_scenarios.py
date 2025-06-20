def test_start_scenario(client, session_manager, isolated_data_dir, character_79e55c14):
    """
    ### test_start_scenario
    **Description :** Teste le démarrage d'un scénario avec nettoyage automatique de session.
    **Paramètres :**
    - `client` (TestClient) : Client FastAPI pour les tests d'API.
    - `session_manager` (SessionManager) : Gestionnaire de sessions pour le nettoyage automatique.
    - `isolated_data_dir` (Path) : Environnement de données isolé.
    **Retour :** None (assertions sur la réponse JSON).
    """
    import json
    from unittest.mock import patch

    scenario_name = "Les_Pierres_du_Passe.md"
    character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
    # Création du fichier scénario dans le dossier temporaire
    scenarios_dir = isolated_data_dir / "scenarios"
    scenarios_dir.mkdir(exist_ok=True)
    (scenarios_dir / scenario_name).write_text("# Test\nContenu du scénario de test.", encoding="utf-8")
    with patch("back.services.scenario_service.get_data_dir", return_value=str(isolated_data_dir)):
        response = client.post("/api/scenarios/start", json={
            "scenario_name": scenario_name,
            "character_id": character_id
        })
        if response.status_code == 200:
            response_data = response.json()
            if "session_id" in response_data:
                session_manager.track_session(response_data["session_id"])
            assert "démarré avec succès" in response_data["message"]
        else:
            assert response.status_code in [200, 409]

def test_start_scenario_returns_session_id(client, session_manager, isolated_data_dir, character_79e55c14):
    """
    ### test_start_scenario_returns_session_id
    **Description:** Vérifie que l'endpoint /api/scenarios/start retourne bien un id de session, le nom du scénario et l'id du personnage.
    **Paramètres :**
    - `client` (TestClient) : Client FastAPI pour les tests d'API.
    - `session_manager` (SessionManager) : Gestionnaire de sessions pour le nettoyage automatique.
    - `isolated_data_dir` (Path) : Environnement de données isolé.
    **Retour :** None (assertions sur la réponse JSON).
    """
    import uuid
    import json
    from unittest.mock import patch

    scenario_name = "Les_Pierres_du_Passe.md"
    character_id = str(uuid.uuid4())
    # Création du fichier scénario dans le dossier temporaire
    scenarios_dir = isolated_data_dir / "scenarios"
    scenarios_dir.mkdir(exist_ok=True)
    (scenarios_dir / scenario_name).write_text("# Test\nContenu du scénario de test.", encoding="utf-8")
    with patch("back.services.scenario_service.get_data_dir", return_value=str(isolated_data_dir)):
        response = client.post("/api/scenarios/start", json={
            "scenario_name": scenario_name,
            "character_id": character_id
        })
        assert response.status_code == 200
        response_data = response.json()
        session_manager.track_session(response_data["session_id"])
        assert "session_id" in response_data
        assert "scenario_name" in response_data
        assert "character_id" in response_data
        assert response_data["scenario_name"] == scenario_name
        assert response_data["character_id"] == character_id

# def test_play_scenario_returns_llm_response(tmp_path, monkeypatch, client):
#     """
#     ### test_play_scenario_returns_llm_response
#     **Description:** Vérifie que l'endpoint /api/scenarios/play retourne bien tous les nouveaux messages générés (delta complet) dans la clé 'responses' et persiste l'historique.
#     **Paramètres :**
#     - `tmp_path` (Path) : Dossier temporaire pytest pour stocker les fichiers de session.
#     - `monkeypatch` (pytest fixture) : Pour patcher les chemins d'accès aux dossiers de données.
#     - `client` (TestClient) : Client FastAPI pour les tests d'API.
#     **Retour :** None (assertions sur la réponse JSON).
#     """
#     import uuid
#     import os
#     from unittest.mock import patch, MagicMock

#     session_id = str(uuid.uuid4())
#     scenario_name = "TestScenario.md"
#     character_id = str(uuid.uuid4())

#     # Préparer le dossier scénario temporaire
#     scenarios_dir = tmp_path / "scenarios"
#     scenarios_dir.mkdir()
#     (scenarios_dir / scenario_name).write_text("# Test\nContenu du scénario de test.", encoding="utf-8")

#     # Créer les fichiers de session pour simuler une session existante
#     sessions_dir = tmp_path / "sessions" / session_id
#     sessions_dir.mkdir(parents=True)
#     (sessions_dir / "character.txt").write_text(character_id, encoding="utf-8")
#     (sessions_dir / "scenario.txt").write_text(scenario_name, encoding="utf-8")

#     # Patch le chemin de base pour pointer sur le dossier temporaire
#     import back.services.scenario_service as scenario_service
#     base_dir = tmp_path
#     monkeypatch.setattr(scenario_service.os.path, "abspath", lambda path: str(base_dir) if "data" in path else path)
#     monkeypatch.setattr(scenario_service.os.path, "join", os.path.join)
#     monkeypatch.setattr(scenario_service.os.path, "exists", os.path.exists)
#     monkeypatch.setattr(scenario_service.os, "makedirs", os.makedirs)

#     # Mock de l'agent LLM pour éviter les appels réels à OpenAI
#     class DummyAgent:
#         def run(self, *args, **kwargs):
#             return {"messages": [
#                 {"role": "tool", "text": "Résultat d'outil"},
#                 {"role": "assistant", "text": "Réponse finale du LLM"}
#             ]}
#         _store = None
#     mock_agent = DummyAgent()
#     mock_store = MagicMock()
#     mock_agent._store = mock_store
#     mock_store.load.return_value = []
#     with patch('back.routers.scenarios.CharacterService.get_character') as mock_char_service, \
#          patch('back.routers.scenarios.build_gm_agent_pydantic', return_value=(mock_agent, mock_store)):
#         mock_character = {"name": "Test Character", "hp": 42}
#         mock_char_service.return_value = mock_character
#         response = client.post(f"/api/scenarios/play?session_id={session_id}", json={"message": "Je fouille la pièce."})
#         assert response.status_code == 200
#         data = response.json()
#         assert "responses" in data
#         assert isinstance(data["responses"], list)
#         # Vérifie que chaque élément du delta est bien un dict (issu de model_dump)
#         for msg in data["responses"]:
#             assert isinstance(msg, dict)
#             assert "role" in msg
#             assert "text" in msg

def test_start_scenario_with_llm_response(tmp_path, monkeypatch, client):
    """
    ### test_start_scenario_with_llm_response
    **Description:** Vérifie que l'endpoint /api/scenarios/start retourne bien une réponse du LLM en plus des informations de session.
    **Paramètres :**
    - `tmp_path` (Path) : Dossier temporaire pytest pour stocker les fichiers de session.
    - `monkeypatch` (pytest fixture) : Pour patcher les chemins d'accès aux dossiers de données.
    - `client` (TestClient) : Client FastAPI pour les tests d'API.
    **Retour :** None (assertions sur la réponse JSON).
    """
    import uuid
    import os
    from unittest.mock import patch, MagicMock
    
    scenario_name = "TestScenario.md"
    character_id = str(uuid.uuid4())
    
    # Préparer le dossier scénario temporaire
    scenarios_dir = tmp_path / "scenarios"
    scenarios_dir.mkdir()
    (scenarios_dir / scenario_name).write_text("# Test\nContenu du scénario de test.", encoding="utf-8")
    
    # Patch le chemin de base pour pointer sur le dossier temporaire
    import back.services.scenario_service as scenario_service
    base_dir = tmp_path
    monkeypatch.setattr(scenario_service.os.path, "abspath", lambda path: str(base_dir) if "data" in path else path)
    monkeypatch.setattr(scenario_service.os.path, "join", os.path.join)
    monkeypatch.setattr(scenario_service.os.path, "exists", os.path.exists)
    monkeypatch.setattr(scenario_service.os, "makedirs", os.makedirs)
    
    # Mock de l'agent LLM pour éviter les appels réels à OpenAI
    mock_agent = MagicMock()
    mock_message = MagicMock()
    mock_message.text = "Bienvenue dans le scénario ! Vous vous trouvez à l'entrée d'une mystérieuse caverne..."
    mock_agent.run.return_value = {"messages": [MagicMock(), mock_message]}  # Le dernier message est la réponse
    mock_store = MagicMock()
    mock_agent._store = mock_store
    mock_store.load.return_value = []
      # Patch pour éviter l'appel réel au service de personnage
    with patch('back.routers.scenarios.CharacterService.get_character') as mock_char_service, \
         patch('back.routers.scenarios.build_gm_agent_pydantic', return_value=(mock_agent, mock_store)):
        
        # Mock du personnage
        mock_character = MagicMock()
        mock_character.json.return_value = '{"name": "Test Character"}'
        mock_char_service.return_value = mock_character
        
        # Appel API
        response = client.post("/api/scenarios/start", json={"scenario_name": scenario_name, "character_id": character_id})
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérifier les informations de session
        assert "session_id" in data
        assert data["scenario_name"] == scenario_name
        assert data["character_id"] == character_id
        assert data["message"].startswith("Scénario")
        
        # Vérifier la réponse du LLM
        assert "llm_response" in data
        assert isinstance(data["llm_response"], str)
        assert len(data["llm_response"]) > 0

def test_start_scenario_prevents_duplicate_session(tmp_path, monkeypatch, client):
    """
    ### test_start_scenario_prevents_duplicate_session
    **Description:** Vérifie que l'endpoint /api/scenarios/start empêche de créer une session duplicatée.
    **Paramètres :**
    - `tmp_path` (Path) : Dossier temporaire pytest pour stocker les fichiers de session.
    - `monkeypatch` (pytest fixture) : Pour patcher les chemins d'accès aux dossiers de données.
    - `client` (TestClient) : Client FastAPI pour les tests d'API.
    **Retour :** None (assertions sur le code de statut HTTP).
    """
    import uuid
    import os
    
    scenario_name = "TestScenario.md"
    character_id = str(uuid.uuid4())
    
    # Préparer le dossier scénario temporaire
    scenarios_dir = tmp_path / "scenarios"
    scenarios_dir.mkdir()
    (scenarios_dir / scenario_name).write_text("# Test\nContenu du scénario de test.", encoding="utf-8")
    
    # Créer une session existante
    sessions_dir = tmp_path / "sessions"
    session_id = str(uuid.uuid4())
    session_dir = sessions_dir / session_id
    session_dir.mkdir(parents=True)
    (session_dir / "character.txt").write_text(character_id, encoding="utf-8")
    (session_dir / "scenario.txt").write_text(scenario_name, encoding="utf-8")
    
    # Patch le chemin de base pour pointer sur le dossier temporaire
    import back.services.scenario_service as scenario_service
    base_dir = tmp_path
    monkeypatch.setattr(scenario_service.os.path, "abspath", lambda path: str(base_dir) if "data" in path else path)
    monkeypatch.setattr(scenario_service.os.path, "join", os.path.join)
    monkeypatch.setattr(scenario_service.os.path, "exists", os.path.exists)
    monkeypatch.setattr(scenario_service.os, "makedirs", os.makedirs)
    
    # Premier appel - doit réussir (si aucune session n'existait avant)
    # Mais comme nous avons créé une session manuellement, cela doit échouer
    response = client.post("/api/scenarios/start", json={"scenario_name": scenario_name, "character_id": character_id})
    
    # Vérifier que la tentative de création d'une session dupliquée échoue
    assert response.status_code == 409
    assert "Une session existe déjà" in response.json()["detail"]

def test_list_active_sessions(client, session_manager, isolated_data_dir, monkeypatch, character_79e55c14):
    """
    ### test_list_active_sessions
    **Description :** Teste la récupération de la liste des sessions actives avec les informations du scénario et du personnage.
    **Paramètres :**
    - `client` (TestClient) : Client FastAPI pour les tests d'API.
    - `session_manager` (SessionManager) : Gestionnaire de sessions pour le nettoyage automatique.
    - `isolated_data_dir` (Path) : Environnement de données isolé.
    - `monkeypatch` (pytest fixture) : Pour patcher les chemins d'accès aux dossiers de données.
    **Retour :** None (assertions sur la réponse JSON).
    """
    import uuid
    import os
    import json
    # Utiliser un UUID fixe pour garantir la cohérence
    character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
    scenario_name = "Les_Pierres_du_Passe.md"
    characters_dir = isolated_data_dir / "characters"
    characters_dir.mkdir(exist_ok=True)
    state = {
        "id": character_id,
        "name": "Test Hero Sessions",
        "race": "Humain",
        "culture": "Rurale",
        
        "caracteristiques": {
            "Force": 10,
            "Constitution": 10,
            "Agilite": 10,
            "Rapidite": 10,
            "Volonte": 10,
            "Raisonnement": 10,
            "Intuition": 10,
            "Presence": 10
        },
        "competences": {"Athletisme": 5},
        "hp": 100,
        "xp": 0,
        "gold": 0,
        "inventory": [],
        "spells": [],
        "culture_bonuses": {"Endurance": 1}
    }
    test_character = {"state": state}
    (characters_dir / f"{character_id}.json").write_text(json.dumps(test_character), encoding="utf-8")
    # Patch le chemin de base pour pointer sur le dossier temporaire
    import back.services.session_service as session_service
    base_dir = isolated_data_dir
    monkeypatch.setattr(session_service.os.path, "abspath", lambda path: str(base_dir) if "data" in path else path)
    monkeypatch.setattr(session_service.os.path, "join", os.path.join)
    monkeypatch.setattr(session_service.os.path, "exists", os.path.exists)
    monkeypatch.setattr(session_service.os, "makedirs", os.makedirs)
    
    # Création du scénario pour le personnage de test
    scenarios_dir = isolated_data_dir / "scenarios"
    scenarios_dir.mkdir(exist_ok=True)
    (scenarios_dir / scenario_name).write_text("# Test\nContenu du scénario de test.", encoding="utf-8")
    start_response = client.post("/api/scenarios/start", json={
        "scenario_name": scenario_name,
        "character_id": character_id
    })
    if start_response.status_code == 200:
        session_data = start_response.json()
        session_manager.track_session(session_data["session_id"])
        sessions_response = client.get("/api/scenarios/sessions")
        assert sessions_response.status_code == 200
        sessions_data = sessions_response.json()
        assert "sessions" in sessions_data
        assert isinstance(sessions_data["sessions"], list)
        sessions = sessions_data["sessions"]
        # Vérifie la présence d’une session avec le bon character_id et scenario_name
        found = any(
            s.get("character_id") == session_data["character_id"]
            and s.get("scenario_name") == session_data["scenario_name"]
            for s in sessions
        )
        assert found, (
            f"Aucune session avec character_id={session_data['character_id']} et scenario_name={session_data['scenario_name']} dans la liste.\n"
            f"Sessions trouvées : {sessions}"
        )
    else:
        # Si la session existe déjà, au moins vérifier que l'endpoint fonctionne
        sessions_response = client.get("/api/scenarios/sessions")
        assert sessions_response.status_code == 200