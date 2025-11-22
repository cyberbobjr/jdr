import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from back.services.equipment_service import EquipmentService
from back.models.domain.character import Character, Stats, Skills, CombatStats, Equipment
from back.models.domain.items import EquipmentItem

@pytest.fixture
def mock_data_service():
    return MagicMock()

@pytest.fixture
def equipment_service(mock_data_service):
    return EquipmentService(mock_data_service)

@pytest.fixture
def mock_character():
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

def test_decrease_item_quantity_success(equipment_service, mock_character):
    # Add an item with quantity 5
    item = EquipmentItem(
        id=str(uuid4()),
        name="Arrows (20)",
        category="consumable",
        cost_gold=0, cost_silver=2, cost_copper=0,
        weight=1.0,
        quantity=5,
        equipped=False
    )
    mock_character.equipment.consumables.append(item)
    
    # Decrease by 1
    equipment_service.decrease_item_quantity(mock_character, "Arrows (20)", 1)
    
    assert item.quantity == 4
    assert len(mock_character.equipment.consumables) == 1
    equipment_service.data_service.save_character.assert_called_once()

def test_decrease_item_quantity_removal(equipment_service, mock_character):
    # Add an item with quantity 1
    item = EquipmentItem(
        id=str(uuid4()),
        name="Potion",
        category="consumable",
        cost_gold=10, cost_silver=0, cost_copper=0,
        weight=0.5,
        quantity=1,
        equipped=False
    )
    mock_character.equipment.consumables.append(item)
    
    # Decrease by 1
    equipment_service.decrease_item_quantity(mock_character, "Potion", 1)
    
    assert len(mock_character.equipment.consumables) == 0
    equipment_service.data_service.save_character.assert_called_once()

def test_decrease_item_quantity_multiple_removal(equipment_service, mock_character):
    # Add an item with quantity 5
    item = EquipmentItem(
        id=str(uuid4()),
        name="Arrows",
        category="consumable",
        cost_gold=0, cost_silver=0, cost_copper=0,
        weight=0.1,
        quantity=5,
        equipped=False
    )
    mock_character.equipment.consumables.append(item)
    
    # Decrease by 5
    equipment_service.decrease_item_quantity(mock_character, "Arrows", 5)
    
    assert len(mock_character.equipment.consumables) == 0
    equipment_service.data_service.save_character.assert_called_once()

def test_decrease_item_quantity_not_found(equipment_service, mock_character):
    # Decrease non-existent item
    equipment_service.decrease_item_quantity(mock_character, "NonExistent", 1)
    
    # Should not crash, should not save
    equipment_service.data_service.save_character.assert_not_called()

def test_decrease_item_quantity_case_insensitive(equipment_service, mock_character):
    # Add an item
    item = EquipmentItem(
        id=str(uuid4()),
        name="Arrows",
        category="consumable",
        cost_gold=0, cost_silver=0, cost_copper=0,
        weight=0.1,
        quantity=5,
        equipped=False
    )
    mock_character.equipment.consumables.append(item)
    
    # Decrease using lowercase
    equipment_service.decrease_item_quantity(mock_character, "arrows", 1)
    
    assert item.quantity == 4
    equipment_service.data_service.save_character.assert_called_once()

def test_increase_item_quantity_success(equipment_service, mock_character):
    # Add an item with quantity 5
    item = EquipmentItem(
        id=str(uuid4()),
        name="Arrows (20)",
        category="consumable",
        cost_gold=0, cost_silver=2, cost_copper=0,
        weight=1.0,
        quantity=5,
        equipped=False
    )
    mock_character.equipment.consumables.append(item)
    
    # Increase by 10
    equipment_service.increase_item_quantity(mock_character, "Arrows (20)", 10)
    
    assert item.quantity == 15
    assert len(mock_character.equipment.consumables) == 1
    equipment_service.data_service.save_character.assert_called_once()

def test_increase_item_quantity_not_found(equipment_service, mock_character):
    # Increase non-existent item
    equipment_service.increase_item_quantity(mock_character, "NonExistent", 5)
    
    # Should not crash, should not save
    equipment_service.data_service.save_character.assert_not_called()

def test_increase_item_quantity_case_insensitive(equipment_service, mock_character):
    # Add an item
    item = EquipmentItem(
        id=str(uuid4()),
        name="Arrows",
        category="consumable",
        cost_gold=0, cost_silver=0, cost_copper=0,
        weight=0.1,
        quantity=5,
        equipped=False
    )
    mock_character.equipment.consumables.append(item)
    
    # Increase using different case
    equipment_service.increase_item_quantity(mock_character, "ARROWS", 3)
    
    assert item.quantity == 8
    equipment_service.data_service.save_character.assert_called_once()
