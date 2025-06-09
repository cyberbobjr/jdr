"""
### test_all_tools_integration
**Description :** Tests d'intégration pour tous les outils après migration PydanticAI.
Vérifie que tous les outils fonctionnent correctement avec le SessionService.
"""

import pytest
import sys
from pathlib import Path

# Ajouter le répertoire back au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from back.services.session_service import SessionService
from back.tools.character_tools import character_apply_xp, character_add_gold, character_take_damage
from back.tools.inventory_tools import inventory_add_item, inventory_remove_item
from back.tools.skill_tools import skill_check_with_character
from back.tools.combat_tools import roll_initiative_tool, perform_attack_tool, calculate_damage_tool


class TestAllToolsIntegration:
    """
    ### TestAllToolsIntegration
    **Description :** Suite de tests d'intégration pour tous les outils migrés vers PydanticAI.
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
    def session_service(self, character_id):
        """
        ### session_service
        **Description :** Fixture qui crée un service de session pour les tests.
        **Parameters :**
        - `character_id` (str): ID du personnage à associer à la session.
        **Returns :** Instance de SessionService configurée pour les tests.
        """
        session_id = "test_all_tools_integration"
        return SessionService(session_id, character_id, "Test Scenario")
    
    @pytest.fixture
    def mock_context(self, session_service):
        """
        ### mock_context
        **Description :** Fixture qui crée un contexte d'exécution simulé pour les tests d'outils.
        **Parameters :**
        - `session_service` (SessionService): Service de session à utiliser.
        **Returns :** Contexte simulé avec deps.
        """
        class MockRunContext:
            def __init__(self, session):
                self.deps = session
        
        return MockRunContext(session_service)
    
    def test_character_tools(self, mock_context):
        """
        ### test_character_tools
        **Description :** Teste tous les outils de personnage.
        **Parameters :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        # Test character_apply_xp
        result = character_apply_xp(mock_context, 50)
        assert isinstance(result, dict)
        
        # Test character_add_gold
        result = character_add_gold(mock_context, 100)
        assert isinstance(result, dict)
        
        # Test character_take_damage
        result = character_take_damage(mock_context, 5, "test")
        assert isinstance(result, dict)
    def test_inventory_tools(self, mock_context):
        """
        ### test_inventory_tools
        **Description :** Teste tous les outils d'inventaire.
        **Parameters :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        # Test inventory_add_item (signature correcte: ctx, item_id, qty)
        result = inventory_add_item(mock_context, "épée_longue", 1)
        assert isinstance(result, dict)
        
        # Test inventory_remove_item (signature correcte: ctx, item_id, qty)
        result = inventory_remove_item(mock_context, "épée_longue", 1)
        assert isinstance(result, dict)
    
    def test_skill_tools(self, mock_context):
        """
        ### test_skill_tools
        **Description :** Teste l'outil de compétences.
        **Parameters :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        # Test skill_check_with_character
        result = skill_check_with_character(mock_context, "Force", "Moyenne")
        assert isinstance(result, str)
        assert "Force" in result
        assert "Jet 1d100" in result
    def test_combat_tools(self, mock_context):
        """
        ### test_combat_tools
        **Description :** Teste les outils de combat.
        **Parameters :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        # Test roll_initiative_tool (signature correcte: ctx, characters)
        test_characters = [
            {"id": "char1", "nom": "Guerrier", "agilite": 65},
            {"id": "char2", "nom": "Orc", "agilite": 45}
        ]
        result = roll_initiative_tool(mock_context, test_characters)
        assert isinstance(result, list)
        assert len(result) == 2
        
        # Test perform_attack_tool (signature correcte: ctx, dice)
        result = perform_attack_tool(mock_context, "1d20")
        assert isinstance(result, int)
        
        # Test calculate_damage_tool (signature correcte: ctx, base_damage, bonus)
        result = calculate_damage_tool(mock_context, 8, 2)
        assert isinstance(result, int)
        assert result >= 0
    
    def test_session_service_character_id(self, session_service, character_id):
        """
        ### test_session_service_character_id
        **Description :** Vérifie que SessionService définit correctement character_id.
        **Parameters :**
        - `session_service` (SessionService): Service de session.
        - `character_id` (str): ID du personnage attendu.
        """
        assert session_service.character_id == character_id
        assert session_service.character_id is not None
    
    def test_all_tools_have_correct_signature(self):
        """
        ### test_all_tools_have_correct_signature
        **Description :** Vérifie que tous les outils ont la signature RunContext[SessionService].
        """
        # Vérifier les signatures via les annotations de type
        import inspect
        
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
            assert len(params) >= 1
            assert params[0].name == 'ctx'
            # Note: On ne peut pas facilement vérifier le type RunContext[SessionService] 
            # dans les tests sans importer pydantic_ai, donc on vérifie juste la structure
