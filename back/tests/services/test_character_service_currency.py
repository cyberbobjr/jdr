import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from back.services.character_service import CharacterService
from back.models.domain.character import Character, Stats, Skills, CombatStats, Equipment

@pytest.fixture
def mock_data_service():
    return MagicMock()

@pytest.fixture
def character_service(mock_data_service):
    char_id = str(uuid4())
    service = CharacterService(char_id, data_service=mock_data_service)
    
    # Setup character with currency
    stats = Stats(strength=10, constitution=10, agility=10, intelligence=10, wisdom=10, charisma=10)
    skills = Skills()
    combat_stats = CombatStats(max_hit_points=50, current_hit_points=50)
    equipment = Equipment(gold=10, silver=5, copper=3)
    
    service.character_data = Character(
        name="Test Hero",
        race="human",
        culture="gondor",
        stats=stats,
        skills=skills,
        combat_stats=combat_stats,
        equipment=equipment
    )
    
    return service

def test_remove_currency_simple(character_service):
    """Test removing currency without conversion"""
    character_service.remove_currency(gold=2, silver=1, copper=2)
    
    assert character_service.character_data.equipment.gold == 8
    assert character_service.character_data.equipment.silver == 4
    assert character_service.character_data.equipment.copper == 1
    character_service.data_service.save_character.assert_called_once()

def test_remove_currency_with_conversion(character_service):
    """Test removing currency with automatic conversion"""
    # Character has: 10G 5S 3C = 1053C total
    # Remove: 0G 8S 0C = 80C
    # Expected: 9G 7S 3C = 973C
    character_service.remove_currency(silver=8)
    
    assert character_service.character_data.equipment.gold == 9
    assert character_service.character_data.equipment.silver == 7
    assert character_service.character_data.equipment.copper == 3

def test_remove_currency_exact_amount(character_service):
    """Test removing exact total currency"""
    # Remove all: 10G 5S 3C
    character_service.remove_currency(gold=10, silver=5, copper=3)
    
    assert character_service.character_data.equipment.gold == 0
    assert character_service.character_data.equipment.silver == 0
    assert character_service.character_data.equipment.copper == 0

def test_remove_currency_insufficient_funds(character_service):
    """Test error when insufficient funds"""
    with pytest.raises(ValueError, match="Insufficient funds"):
        character_service.remove_currency(gold=20)

def test_remove_currency_negative_amount(character_service):
    """Test error with negative amounts"""
    with pytest.raises(ValueError, match="non-negative"):
        character_service.remove_currency(gold=-1)

def test_remove_currency_complex_conversion(character_service):
    """Test complex conversion scenario"""
    # Character has: 10G 5S 3C = 1053C
    # Remove: 5G 7S 5C = 575C
    # Expected: 4G 7S 8C = 478C
    character_service.remove_currency(gold=5, silver=7, copper=5)
    
    assert character_service.character_data.equipment.gold == 4
    assert character_service.character_data.equipment.silver == 7
    assert character_service.character_data.equipment.copper == 8
