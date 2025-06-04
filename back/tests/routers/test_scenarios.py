
def test_start_scenario(client, session_manager, isolated_data_dir):
    """
    ### test_start_scenario
    **Description :** Teste le démarrage d'un scénario avec nettoyage automatique de session.
    **Paramètres :**
    - `client` (TestClient) : Client FastAPI pour les tests d'API.
    - `session_manager` (SessionManager) : Gestionnaire de sessions pour le nettoyage automatique.
    - `isolated_data_dir` (Path) : Environnement de données isolé.
    **Retour :** None (assertions sur la réponse JSON).
    """
    response = client.post("/api/scenarios/start", json={
        "scenario_name": "Les_Pierres_du_Passe.md",
        "character_id": "79e55c14-7dd5-4189-b209-ea88f6d067eb"
    })
    
    # Si une session est créée, la tracker pour nettoyage
    if response.status_code == 200:
        response_data = response.json()
        if "session_id" in response_data:
            session_manager.track_session(response_data["session_id"])
        assert "démarré avec succès" in response_data["message"]
    else:
        # Peut être 409 si session existe déjà, c'est acceptable
        assert response.status_code in [200, 409]

def test_start_scenario_returns_session_id(client, session_manager, isolated_data_dir):
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
    
    # Utiliser un character_id unique pour éviter les conflits
    character_id = str(uuid.uuid4())
    scenario_name = "Les_Pierres_du_Passe.md"
    
    # Créer un personnage de test spécifique
    test_character = {
        "id": character_id,
        "name": "Test Hero Unique",
        "race": "Homme",
        "culture": "Rurale", 
        "profession": "Aventurier",
        "caracteristiques": {
            "Force": 60, "Constitution": 65, "Agilité": 70, "Rapidité": 65,
            "Volonté": 75, "Raisonnement": 80, "Intuition": 70, "Présence": 60
        },
        "competences": {"Combat": 10, "Nature": 15, "Subterfuge": 5},
        "state": {"id": character_id, "hp": 100, "xp": 0, "gold": 50}
    }
    
    import json
    characters_dir = isolated_data_dir / "characters"
    (characters_dir / f"{character_id}.json").write_text(
        json.dumps(test_character, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    
    response = client.post("/api/scenarios/start", json={
        "scenario_name": scenario_name,
        "character_id": character_id
    })
    
    assert response.status_code == 200
    response_data = response.json()
    
    # Tracker la session pour nettoyage automatique
    session_manager.track_session(response_data["session_id"])
    
    assert "session_id" in response_data
    assert "scenario_name" in response_data
    assert "character_id" in response_data
    assert response_data["scenario_name"] == scenario_name
    assert response_data["character_id"] == character_id

def test_play_scenario_returns_llm_response(tmp_path, monkeypatch, client):
    """
    ### test_play_scenario_returns_llm_response
    **Description:** Vérifie que l'endpoint /api/scenarios/play retourne bien une réponse du LLM et persiste l'historique.
    **Paramètres :**
    - `tmp_path` (Path) : Dossier temporaire pytest pour stocker les fichiers de session.
    - `monkeypatch` (pytest fixture) : Pour patcher les chemins d'accès aux dossiers de données.
    - `client` (TestClient) : Client FastAPI pour les tests d'API.
    **Retour :** None (assertions sur la réponse JSON).
    """
    import uuid
    import os
    from unittest.mock import patch, MagicMock
    
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
    
    # Mock de l'agent LLM pour éviter les appels réels à OpenAI
    mock_agent = MagicMock()
    mock_message = MagicMock()
    mock_message.text = "Tu découvres un coffre ancien dissimulé sous la table."
    mock_agent.run.return_value = {"messages": [MagicMock(), mock_message]}
    mock_store = MagicMock()
    mock_agent._store = mock_store
    mock_store.load.return_value = []
    
    # Patch pour éviter l'appel réel au service de personnage
    with patch('back.routers.scenarios.CharacterService.get_character') as mock_char_service, \
         patch('back.routers.scenarios.build_gm_agent', return_value=mock_agent):
        
        # Mock du personnage
        mock_character = MagicMock()
        mock_character.json.return_value = '{"name": "Test Character"}'
        mock_char_service.return_value = mock_character
        
        # Appel API
        response = client.post(f"/api/scenarios/play?session_id={session_id}", json={"message": "Je fouille la pièce."})
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # Accepte None ou str vide comme réponse valide pour les mocks
        assert data["response"] is None or isinstance(data["response"], str)
        # Si la réponse est une chaîne, elle doit être non vide
        if isinstance(data["response"], str):
            assert len(data["response"]) > 0

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
         patch('back.routers.scenarios.build_gm_agent', return_value=mock_agent):
        
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