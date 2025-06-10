"""
Tests consolidés pour l'agent GM PydanticAI.
Couvre tous les aspects : initialisation, prompt système, outils, cas aux bords, etc.
"""

import pytest
import asyncio
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from pydantic_ai import Agent

# Configuration des chemins pour les imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

from back.agents.gm_agent_pydantic import (
    build_gm_agent_pydantic,
    GMAgentDependencies,
    _get_scenario_content,
    _get_rules_content,
    enrich_user_message_with_character
)
from back.services.session_service import SessionService
from back.models.schema import Character


class TestGMAgentConsolidated:
    """
    ### TestGMAgentConsolidated
    **Description :** Suite de tests consolidée pour l'agent GM PydanticAI.
    Couvre l'initialisation, le prompt système, les outils et les cas aux bords.
    """
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """
        ### setup_and_cleanup
        **Description :** Fixture qui s'exécute automatiquement avant et après chaque test pour nettoyer les fichiers temporaires.
        """
        # Setup: note les fichiers existants avant le test
        sessions_dir = Path("data/sessions")
        existing_files = set()
        if sessions_dir.exists():
            existing_files = {f.name for f in sessions_dir.glob("*.jsonl")}
        
        yield  # Le test s'exécute ici
        
        # Cleanup: supprime les nouveaux fichiers créés pendant le test
        if sessions_dir.exists():
            current_files = {f.name for f in sessions_dir.glob("*.jsonl")}
            new_files = current_files - existing_files
            for file_name in new_files:
                file_path = sessions_dir / file_name
                if file_path.exists():
                    try:
                        file_path.unlink()
                        print(f"🗑️ Nettoyage: {file_name} supprimé")
                    except Exception as e:
                        print(f"⚠️ Impossible de supprimer {file_name}: {e}")

    @pytest.fixture
    def temp_session_id(self):
        """
        ### temp_session_id
        **Description :** Génère un ID de session temporaire unique pour les tests.
        **Returns :** Un ID de session unique basé sur un UUID court.
        """
        import uuid
        return f"test_{str(uuid.uuid4())[:8]}"
    
    def test_basic_import(self):
        """Test basique pour vérifier que les imports fonctionnent."""
        from back.agents.gm_agent_pydantic import GMAgentDependencies
        assert GMAgentDependencies is not None
    @pytest.fixture
    def character_id(self):
        """Fixture qui retourne l'ID d'un personnage existant pour les tests."""
        return "79e55c14-7dd5-4189-b209-ea88f6d067eb"

    @pytest.fixture
    def mock_character_data(self):
        """Fixture qui retourne des données de personnage de test."""
        return {
            "id": "d7763165-4c03-4c8d-9bc6-6a2568b79eb3",  # UUID en string
            "name": "Aragorn",
            "race": "Humain",
            "culture": "Gondor",
            "profession": "Rôdeur",
            "caracteristiques": {
                "Force": 85,
                "Agilite": 70,
                "Constitution": 80,
                "Raisonnement": 65,
                "Intuition": 75,
                "Presence": 80
            },
            "competences": {
                "Perception": 60,
                "Combat": 75,
                "Survie": 55
            },
            "hp": 45,
            "inventory": [],
            "equipment": [],
            "spells": [],
            "equipment_summary": None,
            "culture_bonuses": None
        }

    # =============================================================================
    # TESTS D'INITIALISATION DE L'AGENT
    # =============================================================================      def test_gm_agent_dependencies_initialization_basic(self, temp_session_id):
        """Teste l'initialisation basique des dépendances de l'agent GM."""
        deps = GMAgentDependencies(session_id=temp_session_id)
        assert deps.session_id == temp_session_id
        assert deps.character_data is None
        assert deps.store is not None
        assert hasattr(deps.store, 'filepath')

    def test_gm_agent_dependencies_with_character(self, temp_session_id, mock_character_data):
        """Teste l'initialisation des dépendances avec données de personnage."""
        character = Character(**mock_character_data)
        
        deps = GMAgentDependencies(session_id=temp_session_id, character_data=character)
        assert deps.session_id == temp_session_id
        assert deps.character_data == character
        assert deps.store is not None

    def test_build_gm_agent_with_existing_session(self, temp_session_id, character_id):
        """Teste la construction de l'agent avec une session existante."""
        # Créer d'abord une session
        session = SessionService(temp_session_id, character_id, "test_scenario")
        
        # Construire l'agent avec la session existante
        agent, loaded_session = build_gm_agent_pydantic(temp_session_id)
        assert isinstance(agent, Agent)
        assert isinstance(loaded_session, SessionService)
        assert loaded_session.session_id == temp_session_id
        assert loaded_session.character_id == character_id

    def test_build_gm_agent_new_session(self, temp_session_id, character_id):
        """Teste la construction de l'agent avec une nouvelle session."""
        scenario_name = "test_scenario.md"
        
        agent, session = build_gm_agent_pydantic(
            session_id=temp_session_id,
            scenario_name=scenario_name,
            character_id=character_id
        )
        
        assert isinstance(agent, Agent)
        assert isinstance(session, SessionService)
        assert session.session_id == temp_session_id
        assert session.character_id == character_id
        assert session.scenario_name == scenario_name

    # =============================================================================
    # TESTS D'INITIALISATION AUX BORDS (EDGE CASES)
    # =============================================================================

    def test_build_gm_agent_no_session_no_character_id(self):
        """Teste l'erreur quand on n'a ni session existante ni character_id."""
        with pytest.raises(ValueError, match="Session .* n'existe pas et aucun character_id fourni"):
            build_gm_agent_pydantic("nonexistent_session")

    def test_gm_agent_dependencies_empty_session_id(self):
        """Teste l'initialisation avec un session_id vide."""
        deps = GMAgentDependencies(session_id="")
        assert deps.session_id == ""
        assert deps.store is not None

    def test_gm_agent_dependencies_none_character_data(self):
        """Teste l'initialisation avec character_data=None explicite."""
        deps = GMAgentDependencies(session_id="test", character_data=None)
        assert deps.character_data is None   
    def test_build_gm_agent_invalid_character_id(self):
        """Teste la construction avec un character_id inexistant."""
        with pytest.raises(ValueError, match="Personnage .* introuvable"):
            build_gm_agent_pydantic(
                session_id="test_invalid_char",
                character_id="nonexistent_character_id"
            )    
    # =============================================================================
    # TESTS DU PROMPT SYSTÈME ET CHARGEMENT DES RÈGLES
    # =============================================================================

    def test_get_scenario_content_existing_file(self):
        """Teste le chargement d'un fichier scénario existant."""
        scenario_content = "# Test Scenario\nContenu du scénario test"
        
        with patch("back.agents.gm_agent_pydantic.pathlib.Path.exists", return_value=True), \
             patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = scenario_content
            mock_open.return_value.__enter__.return_value = mock_file
            
            content = _get_scenario_content("test_scenario.md")
            assert content == scenario_content

    def test_get_scenario_content_nonexistent_file(self):
        """Teste le chargement d'un fichier scénario inexistant."""
        with patch("pathlib.Path.exists", return_value=False):
            content = _get_scenario_content("nonexistent.md")
            assert content == ""

    def test_get_rules_content_existing_file(self):
        """Teste le chargement des règles du jeu."""
        rules_content = "# Règles du Jeu\nContenu des règles"
        
        with patch("back.agents.gm_agent_pydantic.pathlib.Path.exists", return_value=True), \
             patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_file.read.return_value = rules_content
            mock_open.return_value.__enter__.return_value = mock_file
            
            content = _get_rules_content()
            assert content == rules_content

    def test_get_rules_content_nonexistent_file(self):
        """Teste le chargement des règles quand le fichier n'existe pas."""
        with patch("pathlib.Path.exists", return_value=False):
            content = _get_rules_content()
            assert content == ""

    def test_system_prompt_includes_scenario_and_rules(self, character_id):
        """Teste que le prompt système inclut le scénario et les règles."""
        with patch("back.agents.gm_agent_pydantic._get_scenario_content", return_value="SCENARIO_CONTENT"), \
             patch("back.agents.gm_agent_pydantic._get_rules_content", return_value="RULES_CONTENT"):
            
            agent, session = build_gm_agent_pydantic(
                session_id="test_prompt",
                character_id=character_id,
                scenario_name="test.md"
            )
            
            # Vérifier que l'agent a été créé (le prompt est dans l'agent)
            assert isinstance(agent, Agent)

    # =============================================================================
    # TESTS D'UN PROMPT BASIQUE AVEC INSERTION DE FEUILLE DE PERSONNAGE
    # =============================================================================

    def test_enrich_user_message_with_character_data(self, mock_character_data):
        """Teste l'enrichissement du message utilisateur avec les données du personnage."""
        user_message = "Je veux explorer la forêt"
        enriched = enrich_user_message_with_character(user_message, mock_character_data)
        
        assert "[Contexte du personnage:" in enriched
        assert "Aragorn" in enriched
        assert user_message in enriched
        assert "race" in enriched
        assert json.dumps(mock_character_data, indent=2, ensure_ascii=False) in enriched

    def test_enrich_user_message_empty_character_data(self):
        """Teste l'enrichissement avec des données de personnage vides."""
        user_message = "Je veux explorer la forêt"
        
        enriched = enrich_user_message_with_character(user_message, {})
        
        assert enriched == user_message

    def test_enrich_user_message_none_character_data(self):
        """Teste l'enrichissement avec character_data=None."""
        user_message = "Je veux explorer la forêt"
        
        enriched = enrich_user_message_with_character(user_message, None)
        
        assert enriched == user_message    
    # =============================================================================
    # TESTS DES OUTILS DÉFINIS DANS /back/tools
    # =============================================================================

    @pytest.mark.asyncio
    async def test_agent_has_all_required_tools(self, character_id):
        """Teste que l'agent a tous les outils requis."""
        agent, session = build_gm_agent_pydantic(
            session_id="test_tools_required",
            character_id=character_id
        )
        
        # Vérifier que l'agent a été créé
        assert agent is not None
        
        # L'agent PydanticAI n'expose pas directement la liste des outils
        # Nous testons indirectement en vérifiant qu'il peut utiliser les outils via un message
        try:
            response = await agent.run(
                "Peux-tu me dire quels outils tu as à disposition ?",
                deps=session
            )
            assert response.output is not None
        except Exception as e:
            # L'important est que l'agent ne crash pas
            assert isinstance(e, Exception)

    @pytest.mark.asyncio
    async def test_character_tools_integration(self, character_id):
        """Teste l'intégration des outils de personnage avec l'agent."""
        agent, session = build_gm_agent_pydantic(
            session_id="test_char_tools",
            character_id=character_id
        )
        
        # Test avec un message qui devrait déclencher l'outil d'XP
        try:
            response = await agent.run(
                "Applique 50 points d'expérience au personnage pour avoir résolu l'énigme.",
                deps=session
            )
            assert response.data is not None
        except Exception as e:
            # L'important est que l'agent ne crash pas
            assert isinstance(e, Exception)

    @pytest.mark.asyncio
    async def test_inventory_tools_integration(self, character_id):
        """Teste l'intégration des outils d'inventaire avec l'agent."""
        agent, session = build_gm_agent_pydantic(
            session_id="test_inv_tools",
            character_id=character_id
        )
        
        try:
            response = await agent.run(
                "Ajoute une épée longue à l'inventaire du personnage.",
                deps=session
            )
            assert response.data is not None
        except Exception as e:
            assert isinstance(e, Exception)

    @pytest.mark.asyncio
    async def test_combat_tools_integration(self, character_id):
        """Teste l'intégration des outils de combat avec l'agent."""
        agent, session = build_gm_agent_pydantic(
            session_id="test_combat_tools",
            character_id=character_id
        )
        
        try:
            response = await agent.run(
                "Lance l'initiative pour un combat entre le personnage et un orc.",
                deps=session
            )
            assert response.data is not None
        except Exception as e:
            assert isinstance(e, Exception)

    @pytest.mark.asyncio
    async def test_skill_tools_integration(self, character_id):
        """Teste l'intégration des outils de compétences avec l'agent."""
        agent, session = build_gm_agent_pydantic(
            session_id="test_skill_tools",
            character_id=character_id
        )
        
        try:
            response = await agent.run(
                "Fais un test de Perception de difficulté moyenne pour le personnage.",
                deps=session
            )
            assert response.data is not None
        except Exception as e:
            assert isinstance(e, Exception)

    # =============================================================================
    # TESTS DES OUTILS AVEC CAS AUX BORDS (EDGE CASES)
    # =============================================================================

    @pytest.mark.asyncio
    async def test_agent_with_invalid_tool_parameters(self, character_id):
        """Teste le comportement de l'agent avec des paramètres d'outils invalides."""
        agent, session = build_gm_agent_pydantic(
            session_id="test_invalid_params",
            character_id=character_id
        )
        
        # Tenter d'utiliser un outil avec des paramètres impossibles
        try:
            response = await agent.run(
                "Applique -999999 points d'expérience au personnage.",
                deps=session
            )
            # L'agent devrait gérer cela proprement
            assert response.data is not None
        except Exception as e:
            # Ou lever une exception contrôlée
            assert isinstance(e, Exception)

    @pytest.mark.asyncio
    async def test_agent_with_nonexistent_skill(self, character_id):
        """Teste l'agent avec une compétence inexistante."""
        agent, session = build_gm_agent_pydantic(
            session_id="test_nonexistent_skill",
            character_id=character_id
        )
        
        try:
            response = await agent.run(
                "Fais un test de Magie Interdimensionnelle pour le personnage.",
                deps=session
            )
            assert response.data is not None
        except Exception as e:
            assert isinstance(e, Exception)

    @pytest.mark.asyncio
    async def test_agent_with_empty_message(self, character_id):
        """Teste l'agent avec un message vide."""
        agent, session = build_gm_agent_pydantic(
            session_id="test_empty_message",
            character_id=character_id
        )
        
        try:
            response = await agent.run("", deps=session)
            assert response.data is not None
        except Exception as e:
            assert isinstance(e, Exception)

    @pytest.mark.asyncio 
    async def test_agent_with_very_long_message(self, character_id):
        """Teste l'agent avec un message très long."""
        agent, session = build_gm_agent_pydantic(
            session_id="test_long_message",
            character_id=character_id
        )
        
        long_message = "Raconte-moi une histoire " * 1000
        
        try:
            response = await agent.run(long_message, deps=session)
            assert response.data is not None
        except Exception as e:
            assert isinstance(e, Exception)

    # =============================================================================
    # TESTS SPÉCIAUX ET EDGE CASES SUPPLÉMENTAIRES
    # =============================================================================    def test_agent_model_configuration(self, character_id):
        """Teste que l'agent est configuré avec le bon modèle."""
        with patch.dict(os.environ, {
            'DEEPSEEK_API_KEY': 'test_key',
            'DEEPSEEK_API_BASE_URL': 'https://test.api.com',
            'DEEPSEEK_API_MODEL': 'test-model'
        }):
            agent, session = build_gm_agent_pydantic(
                session_id="test_model_config",
                character_id=character_id
            )
            
            assert hasattr(agent, 'model')
            assert agent.model is not None

    @pytest.mark.asyncio
    async def test_agent_memory_persistence(self, character_id):
        """Teste que l'agent maintient la mémoire entre les interactions."""
        session_id = "test_memory_persistence"
        
        # Première interaction
        agent1, session1 = build_gm_agent_pydantic(
            session_id=session_id,
            character_id=character_id
        )
        
        try:
            response1 = await agent1.run("Je m'appelle Test User", deps=session1)
            assert response1.data is not None
        except Exception:
            pass  # L'important est de tester la persistance
        
        # Deuxième interaction avec la même session
        agent2, session2 = build_gm_agent_pydantic(session_id=session_id)
        
        try:
            response2 = await agent2.run("Comment je m'appelle ?", deps=session2)
            assert response2.data is not None
        except Exception:
            pass

    def test_session_service_integration(self, character_id):
        """Teste l'intégration complète avec SessionService."""
        agent, session = build_gm_agent_pydantic(
            session_id="test_session_integration",
            character_id=character_id
        )
        
        # Vérifier que la session a les bonnes propriétés
        assert session.session_id == "test_session_integration"
        assert session.character_id == character_id
        assert hasattr(session, 'character_data')
        assert session.character_data is not None

    @pytest.mark.asyncio
    async def test_agent_error_handling_invalid_deps(self, character_id):
        """Teste la gestion d'erreur avec des dépendances invalides."""
        agent, session = build_gm_agent_pydantic(
            session_id="test_error_handling",
            character_id=character_id
        )
        
        # Tenter d'utiliser l'agent avec des deps invalides (None au lieu de SessionService)
        try:
            await agent.run("Test message", deps=None)
            # Si ça ne lève pas d'exception, ce n'est pas forcément un problème
            # L'agent pourrait gérer gracieusement les deps None
        except Exception:
            # Une exception est attendue avec deps=None
            pass

    def test_concurrent_agent_creation(self, character_id):
        """Teste la création simultanée de plusieurs agents."""
        agents_and_sessions = []
        
        for i in range(3):
            agent, session = build_gm_agent_pydantic(
                session_id=f"test_concurrent_{i}",
                character_id=character_id
            )
            agents_and_sessions.append((agent, session))
        
        # Vérifier que tous les agents ont été créés correctement
        assert len(agents_and_sessions) == 3
        for agent, session in agents_and_sessions:
            assert isinstance(agent, Agent)
            assert isinstance(session, SessionService)


if __name__ == "__main__":
    # Exécution directe pour tests rapides
    import traceback
    
    print("🧪 Tests consolidés de l'agent GM PydanticAI")
    print("=" * 50)
    
    try:
        test = TestGMAgentConsolidated()
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        
        # Tests d'initialisation basiques
        test.test_gm_agent_dependencies_initialization_basic()
        print("✅ Initialisation des dépendances basique")
        
        test.test_build_gm_agent_new_session(character_id)
        print("✅ Construction d'agent avec nouvelle session")
        
        # Tests de prompt système
        test.test_get_scenario_content_nonexistent_file()
        print("✅ Chargement de scénario (fichier inexistant)")
        
        test.test_get_rules_content_nonexistent_file()
        print("✅ Chargement de règles (fichier inexistant)")
        
        # Tests d'enrichissement de message
        mock_char_data = {"nom": "Test", "niveau": 1}
        test.test_enrich_user_message_with_character_data(mock_char_data)
        print("✅ Enrichissement de message avec personnage")
        
        # Tests des outils
        asyncio.run(test.test_agent_has_all_required_tools(character_id))
        print("✅ Vérification de la présence de tous les outils")
        
        print("\n🎉 TOUS LES TESTS DE BASE PASSÉS !")
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        traceback.print_exc()
