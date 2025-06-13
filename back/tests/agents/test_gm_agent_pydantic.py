"""
Tests pour l'agent GM migré vers PydanticAI (sans appels LLM).
"""

import pytest
from unittest.mock import patch
from back.agents.gm_agent_pydantic import (
    GMAgentDependencies,
    enrich_user_message_with_character
)
from back.agents.PROMPT import get_scenario_content, get_rules_content, build_system_prompt


class TestGMAgentPydantic:
    """
    ### TestGMAgentPydantic  
    **Description :** Tests unitaires pour l'agent GM PydanticAI (sans appels LLM).
    """

    # =============================================================================
    # TESTS DES FONCTIONS DE CHARGEMENT DE CONTENU
    # =============================================================================
    
    def test_get_scenario_content_success(self):
        """Teste le chargement réussi du contenu d'un scénario."""
        scenario_content = "Test scenario content with markdown"
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value=scenario_content):
            content = get_scenario_content("test_scenario.md")
            assert content == scenario_content

    def test_get_scenario_content_file_not_found(self):
        """Teste le comportement quand le fichier de scénario n'existe pas."""
        with patch("pathlib.Path.exists", return_value=False):
            content = get_scenario_content("inexistant.md")
            assert content == ""

    def test_get_scenario_content_with_special_characters(self):
        """Teste le chargement d'un scénario avec des caractères spéciaux."""
        scenario_content = "Scénario avec des caractères spéciaux: àéèùç"
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value=scenario_content):
            content = get_scenario_content("test_scenario.md")
            assert content == scenario_content

    # =============================================================================
    # TESTS DES FONCTIONS DE CHARGEMENT DES RÈGLES
    # =============================================================================
    
    def test_get_rules_content_success(self):
        """Teste le chargement réussi du contenu des règles."""
        rules_content = "Test rules content"
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value=rules_content):
            content = get_rules_content()
            assert content == rules_content

    # =============================================================================
    # TESTS DE CONSTRUCTION DU PROMPT SYSTÈME
    # =============================================================================
    
    def test_build_system_prompt_basic(self):
        """Teste la construction basique du prompt système."""
        prompt = build_system_prompt("Les_Pierres_du_Passe.md")
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_build_system_prompt_with_mock_content(self):
        """Teste la construction du prompt avec du contenu mocké."""
        mock_scenario = "Mock scenario content"
        mock_rules = "Mock rules content"
        
        with patch("back.agents.PROMPT.get_scenario_content", return_value=mock_scenario), \
             patch("back.agents.PROMPT.get_rules_content", return_value=mock_rules):
            prompt = build_system_prompt("test_scenario.md")
            assert mock_scenario in prompt
            assert mock_rules in prompt

    # =============================================================================
    # TESTS D'ENRICHISSEMENT DE MESSAGES
    # =============================================================================
    
    def test_enrich_user_message_with_character_complete(self):
        """Teste l'enrichissement complet d'un message avec données de personnage."""
        character_data = {
            "id": "test-id",
            "name": "Thorin Forgeheart",
            "race": "Nain",
            "profession": "Guerrier",
            "culture": "Montagnes de Fer",
            "attributes": {
                "Vigueur": 16,
                "Agilité": 10,
                "Intelligence": 8,
                "Perception": 12,
                "Volonté": 14,
                "Charisme": 7
            },
            "skills": {
                "Armes blanches": 85,
                "Bouclier": 75,
                "Combat": 80,
                "Forge": 70
            },
            "hp": 50,
            "inventory": ["Épée en fer", "Bouclier rond"],
            "equipment": ["Armure de cuir"],
            "spells": []
        }
        
        message = "Je veux attaquer l'orc avec mon épée."
        enriched = enrich_user_message_with_character(message, character_data)
        
        # Vérifier que le message original est présent
        assert message in enriched
        
        # Vérifier que les données du personnage sont incluses
        assert "Thorin Forgeheart" in enriched
        assert "Nain" in enriched
        assert "Guerrier" in enriched
        assert "Vigueur" in enriched
        assert "Combat" in enriched

    def test_enrich_user_message_empty_character_data(self):
        """Teste l'enrichissement avec des données de personnage minimales."""
        character_data = {
            "id": "minimal-id",
            "name": "Minimal Character",
            "race": "Humain",
            "profession": "Novice",
            "culture": "Test",
            "attributes": {},
            "skills": {},
            "hp": 10,
            "inventory": [],
            "equipment": [],
            "spells": []
        }
        
        message = "Test message"
        enriched = enrich_user_message_with_character(message, character_data)
        
        assert message in enriched
        assert "Minimal Character" in enriched

    # =============================================================================
    # TESTS DE VALIDATION DES MODULES
    # =============================================================================
    
    def test_module_imports_successful(self):
        """Teste que tous les modules nécessaires peuvent être importés."""
        try:
            from back.agents.gm_agent_pydantic import GMAgentDependencies
            from back.agents.PROMPT import build_system_prompt, get_scenario_content, get_rules_content
            assert True  # Si on arrive ici, tous les imports ont réussi
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")

    def test_gm_agent_dependencies_basic_creation(self):
        """Teste la création basique des dépendances GM."""
        session_id = "test-session-123"
        deps = GMAgentDependencies(session_id=session_id)
        
        assert deps.session_id == session_id
        assert deps.character_data is None
        assert deps.store is not None
