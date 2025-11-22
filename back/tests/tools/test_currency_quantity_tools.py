import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from back.services.game_session_service import GameSessionService
from back.tools.character_tools import character_remove_currency
from back.tools.equipment_tools import inventory_increase_quantity
from back.models.domain.character import Character, Stats, Skills, CombatStats, Equipment
from back.models.domain.items import EquipmentItem

@pytest.fixture
def mock_character():
    stats = Stats(strength=10, constitution=10, agility=10, intelligence=10, wisdom=10, charisma=10)
    skills = Skills()
    combat_stats = CombatStats(max_hit_points=50, current_hit_points=50)
    equipment = Equipment(gold=100, silver=5, copper=3)
    
    character = Character(
        name="Test Hero",
        race="human",
        culture="gondor",
        stats=stats,
        skills=skills,
        combat_stats=combat_stats,
        equipment=equipment
    )
    return character

@pytest.fixture
def mock_session_service(mock_character):
    service = MagicMock(spec=GameSessionService)
    service.character_id = str(uuid4())
    
    # Mock character_service
    service.character_service = MagicMock()
    service.character_service.get_character.return_value = mock_character
    service.character_service.remove_currency = MagicMock(return_value=mock_character)
    
    # Mock equipment_service
    service.equipment_service = MagicMock()
    service.equipment_service.increase_item_quantity = MagicMock(return_value=mock_character)
    service.equipment_service.get_equipment_list = MagicMock(return_value=[])
    
    return service

@pytest.fixture
def mock_run_context(mock_session_service):
    mock_model = MagicMock()
    usage = RunUsage(requests=1)
    return RunContext(
        deps=mock_session_service, 
        retry=0, 
        tool_name="test_tool", 
        model=mock_model, 
        usage=usage
    )

# Tests for character_remove_currency

def test_character_remove_currency_success(mock_run_context, mock_character):
    mock_character.equipment.gold = 50
    mock_character.equipment.silver = 3
    mock_character.equipment.copper = 7
    
    result = character_remove_currency(mock_run_context, gold=10, silver=2, copper=5)
    
    assert "message" in result
    assert "Removed 10G 2S 5C" in result["message"]
    assert "currency" in result
    mock_run_context.deps.character_service.remove_currency.assert_called_once_with(10, 2, 5)

def test_character_remove_currency_insufficient_funds(mock_run_context):
    mock_run_context.deps.character_service.remove_currency.side_effect = ValueError("Insufficient funds")
    
    result = character_remove_currency(mock_run_context, gold=1000)
    
    assert "error" in result
    assert "Insufficient funds" in result["error"]

def test_character_remove_currency_service_unavailable(mock_run_context):
    mock_run_context.deps.character_service = None
    
    result = character_remove_currency(mock_run_context, gold=10)
    
    assert "error" in result
    assert "service not available" in result["error"]

# Tests for inventory_increase_quantity

def test_inventory_increase_quantity_success(mock_run_context, mock_character):
    result = inventory_increase_quantity(mock_run_context, "Arrows (20)", amount=5)
    
    assert "message" in result
    assert "Increased Arrows (20) by 5" in result["message"]
    assert "inventory" in result
    mock_run_context.deps.equipment_service.increase_item_quantity.assert_called_once_with(
        mock_character, item_name="Arrows (20)", amount=5
    )

def test_inventory_increase_quantity_service_unavailable(mock_run_context):
    mock_run_context.deps.equipment_service = None
    
    result = inventory_increase_quantity(mock_run_context, "Arrows", amount=1)
    
    assert "error" in result
    assert "service not available" in result["error"]

def test_inventory_increase_quantity_exception(mock_run_context):
    mock_run_context.deps.equipment_service.increase_item_quantity.side_effect = Exception("Increase error")
    
    result = inventory_increase_quantity(mock_run_context, "Arrows", amount=1)
    
    assert "error" in result
    assert "Failed to increase quantity: Increase error" in result["error"]
