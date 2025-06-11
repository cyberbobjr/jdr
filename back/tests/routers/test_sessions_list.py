"""
Test spécifique pour la route list_active_sessions
"""
from unittest.mock import patch


def test_list_active_sessions_simple(client):
    """
    ### test_list_active_sessions_simple
    **Description :** Teste basique de la récupération de la liste des sessions actives.
    **Paramètres :**
    - `client` (TestClient) : Client FastAPI pour les tests d'API.
    **Retour :** None (assertions sur la réponse JSON).
    """
    # Mock du CharacterService pour éviter les erreurs de personnages manquants
    with patch('back.routers.scenarios.CharacterService.get_character') as mock_char_service:
        mock_character = type('MockCharacter', (), {})()
        mock_character.name = "Test Hero Sessions"
        mock_char_service.return_value = mock_character
        
        # Tester l'endpoint directement
        sessions_response = client.get("/api/scenarios/sessions")
        assert sessions_response.status_code == 200
        
        sessions_data = sessions_response.json()
        assert "sessions" in sessions_data
        assert isinstance(sessions_data["sessions"], list)
        
        # Le test passe si l'endpoint fonctionne correctement
        print(f"✅ Endpoint fonctionne - Nombre de sessions: {len(sessions_data['sessions'])}")
