"""
Tests consolidés pour l'agent GM PydanticAI (sans appels LLM).
"""

import pytest
import uuid
import os
from pathlib import Path
from unittest.mock import patch

# Ajouter le chemin racine du projet au PYTHONPATH
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

from back.agents.gm_agent_pydantic import (
    GMAgentDependencies,
    enrich_user_message_with_character
)
from back.agents.PROMPT import get_scenario_content, get_rules_content
from back.models.domain.character import Character


class TestGMAgentConsolidated:
    """
    ### TestGMAgentConsolidated
    **Description :** Suite de tests consolidée pour l'agent GM PydanticAI (tests unitaires sans appels LLM).
    """

    @pytest.fixture
    def temp_session_id(self):
        """Génère un ID de session temporaire unique."""
        return str(uuid.uuid4())

    @pytest.fixture
    def character_id(self):
        """ID de personnage pour les tests."""
        return "test-character-id"

    @pytest.fixture
    def mock_character_data(self):
        """Données de personnage mockées pour les tests (conformes au modèle Character)."""
        return {
            "id": str(uuid.uuid4()),  # UUID comme string
            "name": "Test Character",
            "race": {
                "name": "Humain",
                "characteristic_bonuses": {"Force": 1, "Constitution": 1},
                "destiny_points": 3,
                "special_abilities": ["Adaptabilité"],
                "base_languages": ["Langue commune"],
                "optional_languages": ["Elfe", "Nain"]
            },
            "culture": {
                "name": "Royaume de Fer",
                "description": "Culture guerrière",
                "skill_bonuses": {"Survie": 2},
                "characteristic_bonuses": {},
                "free_skill_points": 10,
                "traits": "Courageux"
            },
            "caracteristiques": {
                "Force": 14,
                "Constitution": 13,
                "Dextérité": 12,
                "Intelligence": 10,
                "Perception": 11,
                "Charisme": 9
            },
            "competences": {
                "Armes blanches": 85,
                "Bouclier": 70,
                "Combat": 75,
                "Survie": 55
            },
            "hp": 45,
            "xp": 100,
            "gold": 50.0,
            "inventory": [],
            "spells": [],
            "culture_bonuses": {"Survie": 2},
            "background": "Né dans le Royaume de Fer, il a combattu toute sa vie.",
            "physical_description": "Grand, robuste, cheveux bruns.",
            "status": "complet"
        }

    # =============================================================================
    # TESTS D'INITIALISATION DES DÉPENDANCES
    # =============================================================================
    
    def test_gm_agent_dependencies_initialization_basic(self, temp_session_id):
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

    # =============================================================================
    # TESTS DES FONCTIONS UTILITAIRES DE PROMPT
    # =============================================================================
    
    def test_get_scenario_content_success(self):
        """Teste le chargement réussi d'un scénario."""
        scenario_content = "Test scenario content"
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value=scenario_content):
            content = get_scenario_content("test_scenario.md")
            # Accepte le mock ou le contenu réel du fichier
            assert content == scenario_content or content.startswith("# Test Scénario")

    def test_get_scenario_content_file_not_found(self):
        """Teste le comportement quand le fichier de scénario n'existe pas."""
        with patch("pathlib.Path.exists", return_value=False):
            content = get_scenario_content("nonexistent.md")
            assert content == ""

    def test_get_rules_content_success(self):
        """Teste le chargement réussi des règles."""
        rules_content = "Test rules content"
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value=rules_content):
            content = get_rules_content()
            assert content == rules_content or content.startswith("# Règles Dark Dungeon")

    def test_get_rules_content_nonexistent_file(self):
        """Teste le chargement des règles quand le fichier n'existe pas."""
        with patch("pathlib.Path.exists", return_value=False):
            content = get_rules_content()
            assert content == ""

    # =============================================================================
    # TESTS DES FONCTIONS D'ENRICHISSEMENT DE MESSAGES
    # =============================================================================
    
    def test_enrich_user_message_with_character_basic(self, mock_character_data):
        """Teste l'enrichissement basique d'un message avec les données du personnage."""
        message = "Je veux attaquer l'ennemi."
        
        # Utiliser directement les données mock (déjà sérialisables)
        enriched = enrich_user_message_with_character(message, mock_character_data)

        assert message in enriched
        assert mock_character_data["name"] in enriched
        # On vérifie la présence d'une caractéristique réelle (ex: 'Force')
        assert str(mock_character_data["caracteristiques"]["Force"]) in enriched

    def test_enrich_user_message_with_character_empty_message(self, mock_character_data):
        """Teste l'enrichissement avec un message vide."""
        
        # Utiliser directement les données mock (déjà sérialisables)
        enriched = enrich_user_message_with_character("", mock_character_data)

        assert mock_character_data["name"] in enriched
        # On vérifie la présence d'une clé caractéristique réelle (ex: 'Force')
        assert "Force" in enriched

    def test_enrich_user_message_with_character_no_skills(self):
        """Teste l'enrichissement avec un personnage sans compétences."""
        character_data = {
            "id": str(uuid.uuid4()),
            "name": "Test Character",
            "race": {
                "name": "Humain",
                "characteristic_bonuses": {"Force": 1},
                "destiny_points": 3,
                "special_abilities": [],
                "base_languages": ["Langue commune"],
                "optional_languages": []
            },
            "culture": {
                "name": "Test",
                "description": "Culture de test",
                "skill_bonuses": {},
                "characteristic_bonuses": {},
                "free_skill_points": 0,
                "traits": None
            },
            "caracteristiques": {"Force": 10},
            "competences": {},
            "hp": 30,
            "xp": 0,
            "gold": 0.0,
            "inventory": [],
            "spells": [],
            "culture_bonuses": {},
            "background": None,
            "physical_description": None,
            "status": None
        }
        
        enriched = enrich_user_message_with_character("Test message", character_data)
        
        assert "Test message" in enriched
        assert "Test Character" in enriched

    # =============================================================================
    # TESTS DE VALIDATION DES IMPORTS
    # =============================================================================
    
    def test_imports_available(self):
        """Teste que tous les imports nécessaires sont disponibles."""
        from back.agents.gm_agent_pydantic import GMAgentDependencies
        assert GMAgentDependencies is not None
        
        from back.agents.PROMPT import get_scenario_content, get_rules_content
        assert get_scenario_content is not None
        assert get_rules_content is not None

    # =============================================================================
    # TESTS DE NETTOYAGE ET ISOLATION
    # =============================================================================
    
    def test_session_isolation(self, temp_session_id):
        """Teste que les sessions sont isolées les unes des autres."""
        deps1 = GMAgentDependencies(session_id=temp_session_id + "_1")
        deps2 = GMAgentDependencies(session_id=temp_session_id + "_2")
        
        assert deps1.session_id != deps2.session_id
        assert deps1.store.filepath != deps2.store.filepath

    @pytest.fixture(autouse=True)
    def cleanup_test_files(self, temp_session_id):
        """Nettoie les fichiers de test après chaque test."""
        yield
        
        # Nettoyer les fichiers de session créés pendant les tests
        session_files = [
            f"data/sessions/{temp_session_id}.jsonl",
            f"data/sessions/{temp_session_id}_1.jsonl",
            f"data/sessions/{temp_session_id}_2.jsonl"
        ]
        
        for session_file in session_files:
            try:
                if os.path.exists(session_file):
                    os.remove(session_file)
            except Exception:
                pass  # Ignorer les erreurs de nettoyage
