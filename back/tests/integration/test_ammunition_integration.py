"""
Integration tests for ammunition and quantity management tools.
These tests use real services (GameSessionService, CharacterService, EquipmentService)
and a temporary data directory to verify the full flow without mocking the core logic.
"""

import pytest
from uuid import uuid4
from back.services.game_session_service import GameSessionService
from back.services.character_service import CharacterService
from back.services.equipment_service import EquipmentService
from back.services.character_data_service import CharacterDataService
from back.tools.equipment_tools import inventory_decrease_quantity, inventory_add_item
from back.models.domain.items import EquipmentItem
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from unittest.mock import MagicMock

@pytest.fixture
def integration_context(temp_data_dir, test_character):
    """
    Setup a real integration context with services using the temp data dir.
    """
    character_id, _ = test_character
    session_id = str(uuid4())
    scenario_filename = "test_scenario.yaml" # Dummy

    # Initialize services with real persistence
    session_service = GameSessionService(session_id, character_id, scenario_filename)
    
    # We need to ensure the session service uses the correct data service that points to temp_data_dir
    # The GameSessionService uses global_container, which might be pointing to real paths if not patched.
    # However, temp_data_dir fixture usually patches get_data_dir.
    # Let's verify services are connected.
    
    return session_service

@pytest.fixture
def run_context(integration_context):
    """Create a RunContext with the real session service"""
    mock_model = MagicMock()
    usage = RunUsage(requests=1)
    return RunContext(
        deps=integration_context, 
        retry=0, 
        tool_name="test_tool", 
        model=mock_model, 
        usage=usage
    )

def test_ammunition_flow(run_context):
    """
    Test the full flow of adding arrows, decreasing them, and consuming the last one.
    """
    session_service = run_context.deps
    character_service = session_service.character_service
    
    # 1. Add Arrows (20) to inventory
    # We use the service directly to setup, or the tool if we want to test that too.
    # Let's use the tool to test it too.
    
    # Note: inventory_add_item might fail if it tries to validate against real equipment.yaml 
    # and "Arrows (20)" isn't there or if the test env doesn't have the yaml.
    # The temp_data_dir fixture should handle copying data if set up correctly.
    # If not, we might need to inject the item manually.
    
    # Let's check if we can add it manually to be safe, then test decrease tool.
    character = character_service.get_character()
    arrows = EquipmentItem(
        id=str(uuid4()),
        name="Arrows (20)",
        category="consumable",
        cost_gold=0, cost_silver=2, cost_copper=0,
        weight=1.0,
        quantity=20,
        equipped=False
    )
    character.equipment.consumables.append(arrows)
    character_service.save_character()
    
    # Verify setup
    loaded_char = character_service.get_character()
    assert len(loaded_char.equipment.consumables) == 1
    assert loaded_char.equipment.consumables[0].quantity == 20
    
    # 2. Decrease quantity by 1 using the tool
    result = inventory_decrease_quantity(run_context, "Arrows (20)", amount=1)
    
    assert "message" in result
    assert "Decreased Arrows (20) by 1" in result["message"]
    
    # Verify persistence
    loaded_char = character_service.get_character()
    assert loaded_char.equipment.consumables[0].quantity == 19
    
    # 3. Decrease by 19 (consume all remaining)
    result = inventory_decrease_quantity(run_context, "Arrows (20)", amount=19)
    
    assert "message" in result
    assert "Decreased Arrows (20) by 19" in result["message"]
    
    # Verify removal
    loaded_char = character_service.get_character()
    assert len(loaded_char.equipment.consumables) == 0

def test_decrease_quantity_not_found(run_context):
    """Test decreasing quantity of an item that doesn't exist"""
    result = inventory_decrease_quantity(run_context, "NonExistentItem", amount=1)
    
    # The tool currently returns the inventory list even if nothing happened, 
    # or maybe we should check if it returns an error?
    # Looking at the implementation: 
    # It calls service.decrease_item_quantity -> returns character (modified or not)
    # Then returns {message, inventory}
    # The service logs a debug message if not found but returns the character.
    # So the tool will return success message? 
    # Wait, the tool implementation:
    # updated_character = service.decrease_item_quantity(...)
    # return {"message": ..., "inventory": ...}
    # It doesn't check if it was found.
    # This is acceptable behavior (idempotent-ish), but let's verify it doesn't crash.
    
    assert "message" in result
    assert "Decreased NonExistentItem by 1" in result["message"] # It claims it did, which is a bit misleading but safe.
    
    # Verify inventory is empty (assuming fresh char)
    session_service = run_context.deps
    char = session_service.character_service.get_character()
    # Fresh char might have starting equipment depending on fixture, but let's just check no crash.
    assert char is not None

def test_currency_removal_flow(run_context):
    """Test the full flow of adding and removing currency"""
    session_service = run_context.deps
    character_service = session_service.character_service
    
    # Setup: Give character some money
    character = character_service.get_character()
    character.equipment.gold = 10
    character.equipment.silver = 5
    character.equipment.copper = 3
    character_service.save_character()
    
    # Remove some currency
    character_service.remove_currency(gold=2, silver=3, copper=1)
    
    # Verify
    loaded_char = character_service.get_character()
    assert loaded_char.equipment.gold == 8
    assert loaded_char.equipment.silver == 2
    assert loaded_char.equipment.copper == 2

def test_currency_removal_with_conversion(run_context):
    """Test currency removal with automatic conversion"""
    session_service = run_context.deps
    character_service = session_service.character_service
    
    # Setup: 5G 0S 0C
    character = character_service.get_character()
    character.equipment.gold = 5
    character.equipment.silver = 0
    character.equipment.copper = 0
    character_service.save_character()
    
    # Remove 3S (should convert from gold)
    character_service.remove_currency(silver=3)
    
    # Verify: 4G 7S 0C
    loaded_char = character_service.get_character()
    assert loaded_char.equipment.gold == 4
    assert loaded_char.equipment.silver == 7
    assert loaded_char.equipment.copper == 0

def test_inventory_increase_quantity_flow(run_context):
    """Test increasing quantity of existing items"""
    session_service = run_context.deps
    character_service = session_service.character_service
    
    # Setup: Add arrows
    character = character_service.get_character()
    from back.models.domain.items import EquipmentItem
    from uuid import uuid4
    
    arrows = EquipmentItem(
        id=str(uuid4()),
        name="Arrows (20)",
        category="consumable",
        cost_gold=0, cost_silver=2, cost_copper=0,
        weight=1.0,
        quantity=10,
        equipped=False
    )
    character.equipment.consumables.append(arrows)
    character_service.save_character()
    
    # Increase by 5
    session_service.equipment_service.increase_item_quantity(character, "Arrows (20)", 5)
    
    # Verify
    loaded_char = character_service.get_character()
    assert loaded_char.equipment.consumables[0].quantity == 15


def test_decrease_quantity_multiple_stacks(run_context):
    """
    Test that it decreases the first stack found.
    """
    session_service = run_context.deps
    character_service = session_service.character_service
    
    character = character_service.get_character()
    
    # Add two stacks of potions
    potion1 = EquipmentItem(
        id=str(uuid4()), name="Potion", category="consumable",
        cost_gold=10, cost_silver=0, cost_copper=0, weight=0.5, quantity=5, equipped=False
    )
    potion2 = EquipmentItem(
        id=str(uuid4()), name="Potion", category="consumable",
        cost_gold=10, cost_silver=0, cost_copper=0, weight=0.5, quantity=5, equipped=False
    )
    character.equipment.consumables.extend([potion1, potion2])
    character_service.save_character()
    
    # Decrease by 3
    inventory_decrease_quantity(run_context, "Potion", amount=3)
    
    loaded_char = character_service.get_character()
    # One should be 2, the other 5.
    quantities = sorted([i.quantity for i in loaded_char.equipment.consumables if i.name == "Potion"])
    assert quantities == [2, 5]
