"""
### test_gm_agent_refactored
**Description :** Tests de l'agent GM après refactorisation complète vers PydanticAI.
Vérifie que l'agent fonctionne correctement avec les outils refactorisés.
"""

import pytest
import sys
from pathlib import Path

# Ajouter le répertoire back au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.gm_agent_pydantic import build_gm_agent_pydantic


class TestGMAgentRefactored:
    """
    ### TestGMAgentRefactored
    **Description :** Suite de tests pour l'agent GM après refactorisation.
    """
    
    @pytest.fixture
    def character_id(self):
        """
        ### character_id
        **Description :** Fixture qui retourne l'ID d'un personnage existant pour les tests.
        **Returns :** ID du personnage de test.
        """
        return "79e55c14-7dd5-4189-b209-ea88f6d067eb"
    
    @pytest.fixture
    def agent_and_session(self, character_id):
        """
        ### agent_and_session
        **Description :** Fixture qui crée un agent GM et sa session.
        **Parameters :**
        - `character_id` (str): ID du personnage à associer.
        **Returns :** Tuple (agent, session).
        """
        session_id = "test_gm_agent_refactored"
        return build_gm_agent_pydantic(session_id, "Test Scenario", character_id)
    
    def test_agent_creation(self, agent_and_session):
        """
        ### test_agent_creation
        **Description :** Vérifie que l'agent peut être créé sans erreur.
        **Parameters :**
        - `agent_and_session` : Tuple (agent, session) de la fixture.
        """
        agent, session = agent_and_session
        
        assert agent is not None
        assert session is not None
        assert session.character_id is not None
    
    def test_agent_has_refactored_tools(self, agent_and_session):
        """
        ### test_agent_has_refactored_tools
        **Description :** Vérifie que l'agent utilise les outils refactorisés.
        **Parameters :**
        - `agent_and_session` : Tuple (agent, session) de la fixture.
        """
        agent, session = agent_and_session
        
        # Vérifier que l'agent a des outils
        assert hasattr(agent, 'tools')
        assert len(agent.tools) > 0
        
        # Vérifier les noms des outils (pas character_perform_skill_check)
        tool_names = [tool.__name__ for tool in agent.tools]
        
        # Outils attendus
        expected_tools = [
            "character_apply_xp",
            "character_add_gold", 
            "character_take_damage",
            "inventory_add_item",
            "inventory_remove_item",
            "skill_check_with_character",  # Pas character_perform_skill_check
            "roll_initiative_tool",
            "perform_attack_tool",
            "resolve_attack_tool",
            "calculate_damage_tool",
            "end_combat_tool"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
        
        # Vérifier que l'outil redondant n'est pas présent
        assert "character_perform_skill_check" not in tool_names
    
    def test_skill_check_via_agent(self, agent_and_session):
        """
        ### test_skill_check_via_agent
        **Description :** Teste un jet de compétence via l'agent.
        **Parameters :**
        - `agent_and_session` : Tuple (agent, session) de la fixture.
        """
        agent, session = agent_and_session
        
        message = "Fais un test de Force avec difficulté Moyenne"
        
        try:
            result = agent.run_sync(message, deps=session)
            
            # Vérifier que la réponse contient des éléments de jet de compétence
            response = result.output if hasattr(result, 'output') else str(result)
            assert isinstance(response, str)
            assert len(response) > 0
            
        except Exception as e:
            pytest.fail(f"Agent failed to process skill check: {str(e)}")
    
    def test_character_action_via_agent(self, agent_and_session):
        """
        ### test_character_action_via_agent
        **Description :** Teste une action de personnage via l'agent.
        **Parameters :**
        - `agent_and_session` : Tuple (agent, session) de la fixture.
        """
        agent, session = agent_and_session
        
        message = "Ajoute 10 pièces d'or au personnage"
        
        try:
            result = agent.run_sync(message, deps=session)
            
            response = result.output if hasattr(result, 'output') else str(result)
            assert isinstance(response, str)
            assert len(response) > 0
            
        except Exception as e:
            pytest.fail(f"Agent failed to process character action: {str(e)}")
    
    def test_inventory_action_via_agent(self, agent_and_session):
        """
        ### test_inventory_action_via_agent
        **Description :** Teste une action d'inventaire via l'agent.
        **Parameters :**
        - `agent_and_session` : Tuple (agent, session) de la fixture.
        """
        agent, session = agent_and_session
        
        message = "Ajoute une épée à l'inventaire"
        
        try:
            result = agent.run_sync(message, deps=session)
            
            response = result.output if hasattr(result, 'output') else str(result)
            assert isinstance(response, str)
            assert len(response) > 0
            
        except Exception as e:
            pytest.fail(f"Agent failed to process inventory action: {str(e)}")
    
    def test_session_service_integration(self, agent_and_session, character_id):
        """
        ### test_session_service_integration
        **Description :** Vérifie l'intégration avec SessionService.
        **Parameters :**
        - `agent_and_session` : Tuple (agent, session) de la fixture.
        - `character_id` (str): ID du personnage attendu.
        """
        agent, session = agent_and_session
        
        # Vérifier que la session a le bon character_id
        assert session.character_id == character_id
        
        # Vérifier que la session peut être utilisée comme deps
        assert hasattr(session, 'character_id')
        assert session.character_id is not None
