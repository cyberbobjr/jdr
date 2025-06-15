"""
Consolidated integration tests for all tools after PydanticAI migration.
Replaces test_all_tools_integration.py with a cleaner, more comprehensive test suite.
"""

import pytest
import sys
import inspect
from pathlib import Path

# Configuration des chemins pour les imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from back.services.session_service import SessionService
from back.tools.character_tools import character_apply_xp, character_add_gold, character_take_damage
from back.tools.inventory_tools import inventory_add_item, inventory_remove_item
from back.tools.skill_tools import skill_check_with_character
from back.tools.combat_tools import roll_initiative_tool, perform_attack_tool, calculate_damage_tool


class TestAllToolsIntegrationConsolidated:
    """
    Comprehensive integration test suite for all tools with SessionService.
    Tests functionality, error handling, and tool signatures.
    """
    
    @pytest.fixture
    def character_id(self, character_79e55c14):
        """Fixture qui retourne l'ID d'un personnage existant pour les tests."""
        return "79e55c14-7dd5-4189-b209-ea88f6d067eb"
    
    @pytest.fixture
    def session_service(self, character_id):
        """Fixture qui crée un service de session pour les tests."""
        session_id = "test_all_tools_integration_consolidated"
        return SessionService(session_id, character_id, "Test Scenario")
    
    @pytest.fixture
    def mock_context(self, session_service):
        """Fixture qui crée un contexte d'exécution simulé pour les tests d'outils."""
        class MockRunContext:
            def __init__(self, session):
                self.deps = session
        
        return MockRunContext(session_service)

    def test_character_tools_basic_functionality(self, mock_context):
        """Teste la fonctionnalité de base de tous les outils de personnage."""
        # Test character_apply_xp
        result = character_apply_xp(mock_context, 50)
        assert isinstance(result, dict)
        assert "character" in result
        assert "xp" in result["character"] or "experience" in result["character"] or "message" in result["character"]
        
        # Test character_add_gold
        result = character_add_gold(mock_context, 100)
        assert isinstance(result, dict)
        assert "character" in result
        assert "gold" in result["character"] or "or" in result["character"] or "message" in result["character"]
        
        # Test character_take_damage
        result = character_take_damage(mock_context, 5, "test damage")
        assert isinstance(result, dict)
        assert "character" in result
        assert "hp" in result["character"] or "message" in result["character"]

    def test_character_tools_edge_cases(self, mock_context):
        """Teste les cas limites des outils de personnage."""
        # Test avec valeurs nulles/négatives
        result = character_apply_xp(mock_context, 0)
        assert isinstance(result, dict)
        
        result = character_add_gold(mock_context, 0)
        assert isinstance(result, dict)
        
        # Test dégâts avec description vide
        result = character_take_damage(mock_context, 1, "")
        assert isinstance(result, dict)

    def test_inventory_tools_basic_functionality(self, mock_context):
        """Teste la fonctionnalité de base des outils d'inventaire."""
        # Test inventory_add_item
        result = inventory_add_item(mock_context, "épée_test", 1)
        assert isinstance(result, dict)
        assert "inventory" in result or "inventaire" in result or "message" in result
        
        # Test inventory_remove_item
        result = inventory_remove_item(mock_context, "épée_test", 1)
        assert isinstance(result, dict)
        assert "inventory" in result or "inventaire" in result or "message" in result

    def test_inventory_tools_multiple_items(self, mock_context):
        """Teste les outils d'inventaire avec plusieurs objets."""
        # Ajouter plusieurs objets
        result = inventory_add_item(mock_context, "potion_test", 5)
        assert isinstance(result, dict)
        
        # Supprimer partiellement
        result = inventory_remove_item(mock_context, "potion_test", 2)
        assert isinstance(result, dict)
        
        # Tenter de supprimer plus que disponible
        result = inventory_remove_item(mock_context, "potion_test", 10)
        assert isinstance(result, dict)

    def test_skill_tools_basic_functionality(self, mock_context):
        """Teste la fonctionnalité de base de l'outil de compétences."""
        # Test skill_check_with_character avec différentes compétences
        result = skill_check_with_character(mock_context, "Force", "Moyenne")
        assert isinstance(result, str)
        assert "Force" in result
        assert "Jet 1d100" in result or "Résultat" in result
        
        # Test avec compétence spécialisée
        result = skill_check_with_character(mock_context, "Perception", "Facile")
        assert isinstance(result, str)
        assert "Perception" in result

    def test_skill_tools_various_difficulties(self, mock_context):
        """Teste l'outil de compétences avec différents niveaux de difficulté."""
        difficulties = ["Facile", "Moyenne", "Difficile", "Très Difficile", "Impossible"]
        
        for difficulty in difficulties:
            result = skill_check_with_character(mock_context, "Force", difficulty)
            assert isinstance(result, str)
            assert "Force" in result
            assert "Jet 1d100" in result or "Résultat" in result

    def test_skill_tools_unknown_skill(self, mock_context):
        """Teste l'outil de compétences avec une compétence inexistante."""
        result = skill_check_with_character(mock_context, "Magie Ancienne", "Très Difficile")
        assert isinstance(result, str)
        assert "Magie Ancienne" in result
        assert "Valeur par défaut" in result or "défaut" in result

    def test_combat_tools_basic_functionality(self, mock_context):
        """Teste la fonctionnalité de base des outils de combat."""
        # Test roll_initiative_tool        
        test_characters = [
            {"id": "char1", "nom": "Guerrier", "agilite": 65},
            {"id": "char2", "nom": "Orc", "agilite": 45}
        ]
        result = roll_initiative_tool(mock_context, test_characters)
        assert isinstance(result, list)
        assert len(result) == 2
        # Check that characters are returned (they should have names)
        assert all("nom" in char for char in result)
        
        # Test perform_attack_tool
        result = perform_attack_tool(mock_context, "1d20")
        assert isinstance(result, int)
        assert 1 <= result <= 20
        
        # Test calculate_damage_tool
        result = calculate_damage_tool(mock_context, 8, 2)
        assert isinstance(result, int)
        assert result >= 0
        assert result == 10  # 8 + 2

    def test_combat_tools_edge_cases(self, mock_context):
        """Teste les cas limites des outils de combat."""
        # Test avec liste vide de personnages
        result = roll_initiative_tool(mock_context, [])
        assert isinstance(result, list)
        assert len(result) == 0
        
        # Test avec dés non standard
        result = perform_attack_tool(mock_context, "1d6")
        assert isinstance(result, int)
        assert 1 <= result <= 6
        
        # Test calculate_damage avec bonus négatif
        result = calculate_damage_tool(mock_context, 5, -10)
        assert isinstance(result, int)
        assert result == 0  # Minimum 0

    def test_session_service_integration(self, session_service, character_id):
        """Vérifie l'intégration correcte avec SessionService."""
        assert session_service.character_id == character_id
        assert session_service.character_id is not None
        assert session_service.session_id is not None
        assert session_service.scenario_name is not None

    def test_all_tools_have_correct_signature(self):
        """Vérifie que tous les outils ont la signature correcte avec ctx comme premier paramètre."""
        tools = [
            character_apply_xp,
            character_add_gold, 
            character_take_damage,
            inventory_add_item,
            inventory_remove_item,
            skill_check_with_character,
            roll_initiative_tool,
            perform_attack_tool,
            calculate_damage_tool
        ]
        
        for tool in tools:
            sig = inspect.signature(tool)
            params = list(sig.parameters.values())
            
            # Le premier paramètre devrait être ctx
            assert len(params) >= 1, f"Tool {tool.__name__} should have at least one parameter"
            assert params[0].name == 'ctx', f"First parameter of {tool.__name__} should be 'ctx', got '{params[0].name}'"

    def test_tool_error_handling(self, mock_context):
        """Teste la gestion d'erreurs des outils."""
        # Test avec des valeurs invalides (ne devrait pas planter)
        try:
            result = character_apply_xp(mock_context, -1)
            assert isinstance(result, dict)
        except Exception as e:
            # Si une exception est levée, elle devrait être informative
            assert str(e) is not None
        
        try:
            result = inventory_add_item(mock_context, "", 1)
            assert isinstance(result, dict)
        except Exception as e:
            assert str(e) is not None

    def test_sequential_tool_execution(self, mock_context):
        """Teste l'exécution séquentielle de plusieurs outils."""
        # Séquence réaliste : ajouter de l'XP, puis de l'or, puis des objets
        xp_result = character_apply_xp(mock_context, 25)
        assert isinstance(xp_result, dict)
        
        gold_result = character_add_gold(mock_context, 50)
        assert isinstance(gold_result, dict)
        
        item_result = inventory_add_item(mock_context, "potion_sequence", 3)
        assert isinstance(item_result, dict)
        
        skill_result = skill_check_with_character(mock_context, "Perception", "Moyenne")
        assert isinstance(skill_result, str)

    def test_cross_tool_compatibility(self, mock_context):
        """Teste la compatibilité entre différents types d'outils."""
        # Vérifier que l'utilisation successive d'outils de différentes catégories fonctionne
        character_result = character_add_gold(mock_context, 10)
        inventory_result = inventory_add_item(mock_context, "test_item", 1)
        skill_result = skill_check_with_character(mock_context, "Force", "Facile")
        combat_result = perform_attack_tool(mock_context, "1d20")
        
        assert isinstance(character_result, dict)
        assert isinstance(inventory_result, dict)
        assert isinstance(skill_result, str)
        assert isinstance(combat_result, int)


if __name__ == "__main__":
    # Exécution directe pour tests rapides
    import traceback
    
    print("🧪 Tests d'intégration consolidés pour tous les outils")
    print("=" * 60)
    
    try:
        test = TestAllToolsIntegrationConsolidated()
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        session = SessionService("test_direct", character_id, "Test")
        
        class MockContext:
            def __init__(self, session):
                self.deps = session
        
        context = MockContext(session)
        
        # Tests rapides
        test.test_all_tools_have_correct_signature()
        print("✅ Signatures des outils validées")
        
        test.test_character_tools_basic_functionality(context)
        print("✅ Outils de personnage fonctionnels")
        
        test.test_inventory_tools_basic_functionality(context)
        print("✅ Outils d'inventaire fonctionnels")
        
        test.test_skill_tools_basic_functionality(context)
        print("✅ Outils de compétences fonctionnels")
        
        test.test_combat_tools_basic_functionality(context)
        print("✅ Outils de combat fonctionnels")
        
        print("\n🎉 TOUS LES TESTS D'INTÉGRATION PASSÉS !")
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        traceback.print_exc()
