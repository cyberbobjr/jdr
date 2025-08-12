"""
Tests unitaires pour l'injection de dépendance dans gm_agent_pydantic.
"""

import pytest
from unittest.mock import Mock, patch
from back.agents.gm_agent_pydantic import build_gm_agent_pydantic, create_session_service, create_gm_agent_with_session
from back.services.session_service import SessionService


class TestGMAgentDependencyInjection:
    """
    ### TestGMAgentDependencyInjection
    **Description :** Teste l'injection de dépendance dans build_gm_agent_pydantic.
    """

    def test_build_gm_agent_with_injected_session_service(self):
        """
        ### test_build_gm_agent_with_injected_session_service
        **Description :** Teste que build_gm_agent_pydantic accepte un SessionService injecté.
        """
        # Mock du SessionService
        mock_session_service = Mock(spec=SessionService)
        mock_session_service.scenario_name = "test_scenario.md"
        
        # La fonction devrait accepter le service injecté sans erreur
        with patch('back.agents.gm_agent_pydantic.build_system_prompt') as mock_build_prompt, \
             patch('back.agents.gm_agent_pydantic.Agent') as mock_agent_class:
            
            mock_build_prompt.return_value = "Test prompt"
            mock_agent_instance = Mock()
            mock_agent_class.return_value = mock_agent_instance
            
            result = build_gm_agent_pydantic(mock_session_service)
            
            # Vérifier que l'agent est retourné
            assert result == mock_agent_instance
            
            # Vérifier que le scenario_name du service est utilisé
            mock_build_prompt.assert_called_once_with("test_scenario.md")

    def test_create_session_service_existing_session(self):
        """
        ### test_create_session_service_existing_session
        **Description :** Teste la création d'un service pour une session existante.
        """
        with patch('back.agents.gm_agent_pydantic.SessionService') as mock_session_class:
            mock_session_instance = Mock()
            mock_session_class.return_value = mock_session_instance
            
            result = create_session_service("existing_session")
            
            # Vérifier que SessionService est appelé avec le bon ID
            mock_session_class.assert_called_once_with("existing_session")
            assert result == mock_session_instance

    def test_create_session_service_new_session(self):
        """
        ### test_create_session_service_new_session
        **Description :** Teste la création d'un service pour une nouvelle session.
        """
        with patch('back.agents.gm_agent_pydantic.SessionService') as mock_session_class:
            # Simuler que la première tentative échoue (session n'existe pas)
            # et la seconde réussit (nouvelle session créée)
            mock_session_instance = Mock()
            mock_session_class.side_effect = [ValueError("Session not found"), mock_session_instance]
            
            result = create_session_service("new_session", character_id="char123", scenario_name="test.md")
            
            # Vérifier que SessionService est appelé deux fois
            assert mock_session_class.call_count == 2
            # Premier appel : tentative de chargement
            mock_session_class.assert_any_call("new_session")
            # Deuxième appel : création avec paramètres
            mock_session_class.assert_any_call("new_session", character_id="char123", scenario_name="test.md")
            assert result == mock_session_instance

    def test_create_session_service_error_without_character_id(self):
        """
        ### test_create_session_service_error_without_character_id
        **Description :** Teste qu'une erreur est levée si la session n'existe pas et qu'aucun character_id n'est fourni.
        """
        with patch('back.agents.gm_agent_pydantic.SessionService') as mock_session_class:
            mock_session_class.side_effect = ValueError("Session not found")
            
            with pytest.raises(ValueError, match="Session new_session n'existe pas et aucun character_id fourni"):
                create_session_service("new_session")

    def test_create_gm_agent_with_session_convenience_function(self):
        """
        ### test_create_gm_agent_with_session_convenience_function
        **Description :** Teste la fonction de commodité qui combine la création du service et de l'agent.
        """
        with patch('back.agents.gm_agent_pydantic.create_session_service') as mock_create_service, \
             patch('back.agents.gm_agent_pydantic.build_gm_agent_pydantic') as mock_build_agent:
            
            mock_session_service = Mock()
            mock_agent = Mock()
            mock_create_service.return_value = mock_session_service
            mock_build_agent.return_value = mock_agent
            
            agent, session_service = create_gm_agent_with_session("test_session", "char123", "scenario.md")
            
            # Vérifier que les fonctions sont appelées avec les bons paramètres
            mock_create_service.assert_called_once_with("test_session", "char123", "scenario.md")
            mock_build_agent.assert_called_once_with(mock_session_service)
            
            # Vérifier le retour
            assert agent == mock_agent
            assert session_service == mock_session_service
