import pytest
from unittest.mock import MagicMock, patch
from back.services.character_service import CharacterService
from back.models.domain.character import Character, Stats, CombatStats

@pytest.fixture
def mock_character_data():
    return Character(
        id="123e4567-e89b-12d3-a456-426614174000",
        name="Test Hero",
        race="Human",
        culture="Empire",
        level=1,
        experience_points=0, # Maps to xp property
        equipment={"gold": 100}, # Maps to gold property
        stats=Stats(
            strength=10,
            agility=10,
            constitution=10,
            intelligence=10,
            wisdom=10,
            charisma=10
        ),
        skills={
            "artistic": {},
            "magic_arts": {},
            "athletic": {},
            "combat": {},
            "concentration": {},
            "general": {}
        },
        combat_stats=CombatStats(
            max_hit_points=20,
            current_hit_points=20,
            armor_class=10
        )
    )

@pytest.fixture
def mock_character_service(mock_character_data):
    with patch('back.services.character_service.CharacterDataService') as MockDataService:
        mock_instance = MockDataService.return_value
        mock_instance.load_character.return_value = mock_character_data
        
        service = CharacterService("123e4567-e89b-12d3-a456-426614174000")
        return service

def test_initialization(mock_character_service):
    assert mock_character_service.character_id == "123e4567-e89b-12d3-a456-426614174000"
    assert mock_character_service.character_data.name == "Test Hero"

def test_apply_xp_normal(mock_character_service):
    mock_character_service.apply_xp(100)
    assert mock_character_service.character_data.xp == 100
    assert mock_character_service.character_data.level == 1

def test_apply_xp_level_up(mock_character_service):
    # Threshold is level * 1000. Level 1 -> 1000 XP needed.
    mock_character_service.apply_xp(1000)
    assert mock_character_service.character_data.level == 2
    # Max HP should increase: Const(10)*10 + Level(2)*5 = 100 + 10 = 110
    assert mock_character_service.character_data.combat_stats.max_hit_points == 110
    assert mock_character_service.character_data.combat_stats.current_hit_points == 110

def test_apply_xp_negative(mock_character_service):
    mock_character_service.apply_xp(-50)
    assert mock_character_service.character_data.xp == 0

def test_add_gold(mock_character_service):
    mock_character_service.add_gold(50)
    assert mock_character_service.character_data.gold == 150
    
    mock_character_service.add_gold(-200)
    assert mock_character_service.character_data.gold == 0 # Should not go negative

def test_take_damage(mock_character_service):
    mock_character_service.take_damage(5)
    assert mock_character_service.character_data.hp == 15
    
    mock_character_service.take_damage(20)
    assert mock_character_service.character_data.hp == 0
    assert not mock_character_service.is_alive()

def test_heal(mock_character_service):
    mock_character_service.character_data.hp = 10
    mock_character_service.heal(5)
    assert mock_character_service.character_data.hp == 15
    
    mock_character_service.heal(100) # Overheal
    assert mock_character_service.character_data.hp == 20 # Capped at max

def test_short_rest(mock_character_service):
    # Max HP 20. Short rest heals 25% -> 5 HP.
    mock_character_service.character_data.hp = 10
    mock_character_service.short_rest()
    assert mock_character_service.character_data.hp == 15

def test_long_rest(mock_character_service):
    mock_character_service.character_data.hp = 1
    mock_character_service.long_rest()
    assert mock_character_service.character_data.hp == 20

def test_calculate_max_hp(mock_character_service):
    # Const 10, Level 1 -> 10*10 + 1*5 = 105
    # Wait, fixture has Const 10.
    # Formula in service: constitution * 10 + level * 5
    # 10 * 10 + 1 * 5 = 105.
    # In fixture I set max_hp manually to 20, but calculate_max_hp uses stats.
    calculated = mock_character_service.calculate_max_hp()
    assert calculated == 105
