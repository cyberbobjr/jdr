import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from back.services.game_session_service import GameSessionService
from back.tools.equipment_tools import inventory_buy_item
from back.tools.character_tools import character_add_currency
from back.models.domain.character import Character, Stats, Skills, CombatStats, Equipment

@pytest.fixture
def mock_character():
    """Create a mock character with currency"""
    stats = Stats(strength=10, constitution=10, agility=10, intelligence=10, wisdom=10, charisma=10)
    skills = Skills()
    combat_stats = CombatStats(max_hit_points=50, current_hit_points=50)
    equipment = Equipment(gold=10, silver=5, copper=50) # Total: 1000 + 50 + 50 = 1100 copper
    
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
    """Create a mock GameSessionService"""
    service = MagicMock(spec=GameSessionService)
    service.character_id = str(uuid4())
    
    # Mock character_service
    service.character_service = MagicMock()
    service.character_service.get_character.return_value = mock_character
    service.character_service.save_character = MagicMock()
    
    # Mock equipment_service
    service.equipment_service = MagicMock()
    
    return service

@pytest.fixture
def mock_run_context(mock_session_service):
    """Create a mock RunContext"""
    mock_model = MagicMock()
    usage = RunUsage(requests=1)
    return RunContext(
        deps=mock_session_service, 
        retry=0, 
        tool_name="test_tool", 
        model=mock_model, 
        usage=usage
    )

def test_inventory_buy_item_success_gold_only(mock_run_context, mock_character):
    """Test buying an item costing only gold"""
    # Setup mocks
    mock_item = {"id": "sword", "cost_gold": 2, "cost_silver": 0, "cost_copper": 0}
    mock_run_context.deps.equipment_service.equipment_manager.get_equipment_by_id.return_value = mock_item
    mock_run_context.deps.equipment_service.add_item.return_value = mock_character
    mock_run_context.deps.equipment_service.get_equipment_list.return_value = ["sword"]
    
    # Execute
    result = inventory_buy_item(mock_run_context, "sword", qty=1)
    
    # Assert
    assert "Purchased 1 x sword" in result["message"]
    assert result["transaction"]["cost"]["gold"] == 2
    # Initial: 10G 5S 50C = 1100C. Cost: 2G = 200C. Remaining: 900C.
    # Greedy redistribution: 9G 0S 0C.
    assert mock_character.gold == 9
    assert mock_character.silver == 0
    assert mock_character.copper == 0
    mock_run_context.deps.equipment_service.add_item.assert_called_once()

def test_inventory_buy_item_success_mixed_currency(mock_run_context, mock_character):
    """Test buying an item with mixed currency cost"""
    # Setup mocks
    mock_item = {"id": "dagger", "cost_gold": 0, "cost_silver": 5, "cost_copper": 10}
    mock_run_context.deps.equipment_service.equipment_manager.get_equipment_by_id.return_value = mock_item
    mock_run_context.deps.equipment_service.add_item.return_value = mock_character
    mock_run_context.deps.equipment_service.get_equipment_list.return_value = ["dagger"]
    
    # Execute
    result = inventory_buy_item(mock_run_context, "dagger", qty=1)
    
    # Assert
    assert "Purchased 1 x dagger" in result["message"]
    # Initial: 10G 5S 50C = 1100C. Cost: 0G 5S 10C = 60C. Remaining: 1040C.
    # Greedy redistribution: 10G 4S 0C.
    assert mock_character.gold == 10
    assert mock_character.silver == 4
    assert mock_character.copper == 0

def test_inventory_buy_item_insufficient_funds(mock_run_context, mock_character):
    """Test buying an item with insufficient funds"""
    # Setup mocks
    mock_item = {"id": "expensive_armor", "cost_gold": 100, "cost_silver": 0, "cost_copper": 0}
    mock_run_context.deps.equipment_service.equipment_manager.get_equipment_by_id.return_value = mock_item
    
    # Execute
    result = inventory_buy_item(mock_run_context, "expensive_armor", qty=1)
    
    # Assert
    assert "error" in result
    assert "Insufficient funds" in result["error"]
    mock_run_context.deps.equipment_service.add_item.assert_not_called()

def test_inventory_buy_item_with_conversion(mock_run_context, mock_character):
    """Test buying an item requiring currency conversion"""
    # Initial: 10G 5S 50C. Total Copper: 1100.
    # Cost: 0G 6S 0C (60C).
    # Player has 5S, needs 1S more. Should break 1G into 10S.
    # Result should be: 9G 9S 50C.
    
    # Setup mocks
    mock_item = {"id": "item", "cost_gold": 0, "cost_silver": 6, "cost_copper": 0}
    mock_run_context.deps.equipment_service.equipment_manager.get_equipment_by_id.return_value = mock_item
    mock_run_context.deps.equipment_service.add_item.return_value = mock_character
    mock_run_context.deps.equipment_service.get_equipment_list.return_value = ["item"]
    
    # Execute
    result = inventory_buy_item(mock_run_context, "item", qty=1)
    
    # Assert
    assert "Purchased" in result["message"]
    # Check total value in copper to be safe
    expected_copper = 1100 - 60
    actual_copper = mock_character.equipment.get_total_in_copper()
    assert actual_copper == expected_copper
    
    # Check specific distribution (greedy algorithm)
    # 1040 copper -> 10G 4S 0C
    assert mock_character.gold == 10
    assert mock_character.silver == 4
    assert mock_character.copper == 0

def test_character_add_currency(mock_run_context, mock_character):
    """Test adding currency to character"""
    # Execute
    result = character_add_currency(mock_run_context, gold=5, silver=2, copper=10)
    
    # Assert
    assert "Added 5G 2S 10C" in result["message"]
    # Initial: 10G 5S 50C. Added: 5G 2S 10C. Result: 15G 7S 60C.
    assert mock_character.gold == 15
    assert mock_character.silver == 7
    assert mock_character.copper == 60
    mock_run_context.deps.character_service.save_character.assert_called_once()
