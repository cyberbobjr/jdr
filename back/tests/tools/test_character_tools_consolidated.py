"""
Tests consolidés pour les outils de personnage (character_tools).
Regroupe tous les tests liés à l'XP, l'or, les dégâts et autres attributs de personnage.
"""

import pytest
from pathlib import Path

# Configuration des chemins pour les imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

from back.services.session_service import SessionService
from back.tools.character_tools import character_apply_xp, character_add_gold, character_take_damage


class TestCharacterTools:
    """
    ### TestCharacterTools
    **Description :** Tests consolidés pour tous les outils de gestion des personnages.
    """
    
    @pytest.fixture
    def character_id(self):
        """
        ### character_id
        **Description :** Fixture qui retourne l'ID d'un personnage existant pour les tests.
        **Retour :** ID du personnage de test (str).
        """
        return "79e55c14-7dd5-4189-b209-ea88f6d067eb"
    
    @pytest.fixture
    def session_service(self, character_id):
        """
        ### session_service
        **Description :** Fixture qui crée un service de session pour les tests.
        **Paramètres :**
        - `character_id` (str): ID du personnage à associer à la session.
        **Retour :** Instance de SessionService configurée pour les tests.
        """
        session_id = "test_character_tools"
        return SessionService(session_id, character_id, "Test Scenario")
    
    @pytest.fixture
    def mock_context(self, session_service):
        """
        ### mock_context
        **Description :** Fixture qui crée un contexte d'exécution simulé pour les tests d'outils.
        **Paramètres :**
        - `session_service` (SessionService): Service de session à utiliser.
        **Retour :** Contexte simulé avec deps.
        """
        class MockRunContext:
            def __init__(self, session):
                self.deps = session
        
        return MockRunContext(session_service)
    def test_character_apply_xp(self, mock_context):
        """
        ### test_character_apply_xp
        **Description :** Teste l'ajout d'expérience à un personnage.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        xp_to_add = 100
        
        # Récupérer l'XP initial
        initial_character = mock_context.deps.character_data
        initial_xp = initial_character.get("xp", 0)
        
        # Appliquer l'XP
        result = character_apply_xp(mock_context, xp_to_add)
          # Vérifications
        assert isinstance(result, dict)
        assert "character" in result
        assert "xp" in result["character"]
        # Vérifier que l'XP a augmenté
        assert result["character"]["xp"] >= initial_xp + xp_to_add
    def test_character_add_gold(self, mock_context):
        """
        ### test_character_add_gold
        **Description :** Teste l'ajout d'or à un personnage.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        gold_to_add = 50
        
        # Récupérer l'or initial
        initial_character = mock_context.deps.character_data
        initial_gold = initial_character.get("gold", 0)
        
        # Ajouter l'or
        result = character_add_gold(mock_context, gold_to_add)
          # Vérifications
        assert isinstance(result, dict)
        assert "character" in result
        assert "gold" in result["character"]
        # Vérifier que l'or a augmenté
        assert result["character"]["gold"] >= initial_gold + gold_to_add
    
    def test_character_take_damage(self, mock_context):
        """
        ### test_character_take_damage
        **Description :** Teste l'application de dégâts à un personnage.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        damage_amount = 10
        damage_source = "test_combat"
        
        # Récupérer les HP initiaux
        initial_character = mock_context.deps.character_data
        initial_hp = initial_character.get("hp", 100)
        
        # Appliquer les dégâts
        result = character_take_damage(mock_context, damage_amount, damage_source)
          # Vérifications
        assert isinstance(result, dict)
        assert "character" in result
        assert "hp" in result["character"]
        expected_hp = max(0, initial_hp - damage_amount)
        assert result["character"]["hp"] == expected_hp
    
    def test_character_take_damage_minimum_zero(self, mock_context):
        """
        ### test_character_take_damage_minimum_zero
        **Description :** Teste que les HP ne peuvent pas descendre en dessous de 0.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        # Appliquer des dégâts très importants
        damage_amount = 9999
        
        result = character_take_damage(mock_context, damage_amount, "massive_damage")
          # Vérifications
        assert isinstance(result, dict)
        assert "character" in result
        assert "hp" in result["character"]
        assert result["character"]["hp"] == 0  # Ne peut pas être négatif
    def test_character_apply_xp_multiple_times(self, mock_context):
        """
        ### test_character_apply_xp_multiple_times
        **Description :** Teste l'ajout d'XP en plusieurs fois.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        # Ajouter de l'XP en plusieurs fois
        result1 = character_apply_xp(mock_context, 50)
        result2 = character_apply_xp(mock_context, 30)
          # Vérifications - juste s'assurer que les outils fonctionnent
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
        assert "character" in result1
        assert "character" in result2
        assert "xp" in result1["character"]
        assert "xp" in result2["character"]
        # Le deuxième résultat devrait avoir plus d'XP que le premier
        assert result2["character"]["xp"] >= result1["character"]["xp"]

    def test_character_add_gold_multiple_times(self, mock_context):
        """
        ### test_character_add_gold_multiple_times
        **Description :** Teste l'ajout d'or en plusieurs fois.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        # Ajouter de l'or en plusieurs fois
        result1 = character_add_gold(mock_context, 25)
        result2 = character_add_gold(mock_context, 15)
          # Vérifications - juste s'assurer que les outils fonctionnent
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
        assert "character" in result1
        assert "character" in result2
        assert "gold" in result1["character"]
        assert "gold" in result2["character"]
        # Le deuxième résultat devrait avoir plus d'or que le premier
        assert result2["character"]["gold"] >= result1["character"]["gold"]

    def test_character_damage_and_heal_simulation(self, mock_context):
        """
        ### test_character_damage_and_heal_simulation
        **Description :** Teste une simulation de dégâts.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        # Récupérer les HP initiaux
        initial_character = mock_context.deps.character_data
        initial_hp = initial_character.get("hp", 100)
          # Appliquer des dégâts
        damaged_result = character_take_damage(mock_context, 20, "combat")
        damaged_hp = damaged_result["character"]["hp"]
        
        # Vérifier que les dégâts ont été appliqués (HP diminués ou à 0)
        assert isinstance(damaged_result, dict)
        assert "character" in damaged_result
        assert "hp" in damaged_result["character"]
        assert damaged_hp <= initial_hp
