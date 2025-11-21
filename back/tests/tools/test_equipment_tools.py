import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from back.services.game_session_service import GameSessionService
from back.tools.equipment_tools import inventory_add_item, inventory_remove_item
from back.models.domain.character import Character, Stats, Skills, CombatStats, Equipment


@pytest.fixture
def mock_character():
    """Create a mock character with gold"""
    stats = Stats(strength=10, constitution=10, agility=10, intelligence=10, wisdom=10, charisma=10)
    skills = Skills()
    combat_stats = CombatStats(max_hit_points=50, current_hit_points=50)
    equipment = Equipment(gold=100)
    
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
    service.character_service.add_gold = MagicMock()
    
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


def test_inventory_add_item_free(mock_run_context, mock_character):
    """Test adding a free item to inventory"""
    # Setup mocks
    mock_run_context.deps.equipment_service.add_item.return_value = mock_character
    mock_run_context.deps.equipment_service.get_equipment_list.return_value = ["sword"]
    
    # Execute
    result = inventory_add_item(mock_run_context, "sword", qty=1, cost=0)
    
    # Assert
    assert result["message"] == "Added 1 x sword"
    assert result["inventory"] == ["sword"]
    assert result["transaction"]["cost"] == 0
    mock_run_context.deps.equipment_service.add_item.assert_called_once()
    mock_run_context.deps.character_service.add_gold.assert_not_called()


def test_inventory_add_item_with_cost(mock_run_context, mock_character):
    """Test adding an item with cost deduction"""
    # Setup mocks
    mock_character.equipment.gold = 100
    mock_run_context.deps.equipment_service.add_item.return_value = mock_character
    mock_run_context.deps.equipment_service.get_equipment_list.return_value = ["longsword"]
    
    # Execute
    result = inventory_add_item(mock_run_context, "longsword", qty=1, cost=15)
    
    # Assert
    assert "Added 1 x longsword for 15 gold" in result["message"]
    assert result["transaction"]["cost"] == 15
    mock_run_context.deps.character_service.add_gold.assert_called_once_with(-15)
    mock_run_context.deps.equipment_service.add_item.assert_called_once()


def test_inventory_add_item_insufficient_gold(mock_run_context, mock_character):
    """Test adding an item when player doesn't have enough gold"""
    # Setup mocks
    mock_character.equipment.gold = 5
    
    # Execute
    result = inventory_add_item(mock_run_context, "expensive_sword", qty=1, cost=100)
    
    # Assert
    assert "error" in result
    assert "Not enough gold" in result["error"]
    assert result["transaction"] == "failed"
    mock_run_context.deps.equipment_service.add_item.assert_not_called()


def test_inventory_add_item_french_name_rejected(mock_run_context):
    """Test that French item names are rejected"""
    # Execute
    result = inventory_add_item(mock_run_context, "épée_longue", qty=1, cost=0)
    
    # Assert
    assert "error" in result
    assert "must be in English" in result["error"]
    assert "suggestion" in result
    mock_run_context.deps.equipment_service.add_item.assert_not_called()


def test_inventory_add_item_service_unavailable(mock_run_context):
    """Test error handling when equipment service is unavailable"""
    mock_run_context.deps.equipment_service = None
    
    # Execute
    result = inventory_add_item(mock_run_context, "sword", qty=1, cost=0)
    
    # Assert
    assert "error" in result
    assert "service not available" in result["error"]


def test_inventory_remove_item(mock_run_context, mock_character):
    """Test removing an item from inventory"""
    # Setup mocks
    mock_run_context.deps.equipment_service.remove_item.return_value = mock_character
    mock_run_context.deps.equipment_service.get_equipment_list.return_value = []
    
    # Execute
    result = inventory_remove_item(mock_run_context, "potion", qty=1)
    
    # Assert
    assert result["message"] == "Removed 1 x potion"
    assert result["inventory"] == []
    mock_run_context.deps.equipment_service.remove_item.assert_called_once_with(
        mock_character, item_id="potion", quantity=1
    )


def test_inventory_remove_item_service_unavailable(mock_run_context):
    """Test error handling when equipment service is unavailable"""
    mock_run_context.deps.equipment_service = None
    
    # Execute
    result = inventory_remove_item(mock_run_context, "potion", qty=1)
    
    # Assert
    assert "error" in result
    assert "service not available" in result["error"]


def test_list_available_equipment_all(mock_run_context):
    """Test listing all available equipment"""
    # Setup mocks
    mock_equipment_manager = MagicMock()
    mock_equipment_manager.get_all_equipment.return_value = {
        "weapons": [
            {"id": "longsword", "name": "Longsword", "cost": 15, "weight": 3, "damage": "1d8", "description": "A versatile blade"}
        ],
        "armor": [
            {"id": "leather_armor", "name": "Leather Armor", "cost": 10, "weight": 5, "protection": 2, "description": "Light protection"}
        ],
        "accessories": [],
        "consumables": []
    }
    mock_run_context.deps.equipment_service.equipment_manager = mock_equipment_manager
    
    # Execute
    from back.tools.equipment_tools import list_available_equipment
    result = list_available_equipment(mock_run_context, category="all")
    
    # Assert
    assert "items" in result
    assert "weapons" in result["items"]
    assert "armor" in result["items"]
    assert len(result["items"]["weapons"]) == 1
    assert result["items"]["weapons"][0]["item_id"] == "longsword"
    assert result["items"]["weapons"][0]["cost"] == 15
    assert "summary" in result


def test_list_available_equipment_by_category(mock_run_context):
    """Test listing equipment filtered by category"""
    # Setup mocks
    mock_equipment_manager = MagicMock()
    mock_equipment_manager.get_all_equipment.return_value = {
        "weapons": [
            {"id": "sword", "name": "Sword", "cost": 10, "weight": 2, "damage": "1d6", "description": "Basic sword"}
        ],
        "armor": [],
        "accessories": [],
        "consumables": []
    }
    mock_run_context.deps.equipment_service.equipment_manager = mock_equipment_manager
    
    # Execute
    from back.tools.equipment_tools import list_available_equipment
    result = list_available_equipment(mock_run_context, category="weapons")
    
    # Assert
    assert "items" in result
    assert "weapons" in result["items"]
    assert "armor" not in result["items"]
    assert result["category_filter"] == "weapons"


def test_list_available_equipment_invalid_category(mock_run_context):
    """Test error handling for invalid category"""
    # Setup mocks
    mock_equipment_manager = MagicMock()
    mock_run_context.deps.equipment_service.equipment_manager = mock_equipment_manager
    
    # Execute
    from back.tools.equipment_tools import list_available_equipment
    result = list_available_equipment(mock_run_context, category="invalid")
    
    # Assert
    assert "error" in result
    assert "Invalid category" in result["error"]

