"""
Integration tests for reward flows (XP and gold).
"""

import pytest
from back.services.character_service import CharacterService
from back.services.character_data_service import CharacterDataService
from back.tests.integration.helpers import assert_character_state, load_character_from_file


def test_add_xp(temp_data_dir, test_character):
    """Test adding XP to character with real persistence"""
    character_id, character_data = test_character
    
    # Initialize services
    data_service = CharacterDataService()
    char_service = CharacterService(character_id, data_service=data_service)
    
    # Initial state
    assert character_data.experience_points == 0
    
    # Add XP
    char_service.apply_xp(100)
    
    # Verify in-memory state
    updated_character = char_service.get_character()
    assert updated_character.experience_points == 100
    
    # Verify persistence
    saved_data = load_character_from_file(temp_data_dir, character_id)
    assert saved_data["experience_points"] == 100


def test_add_gold(temp_data_dir, test_character):
    """Test adding gold to character with real persistence"""
    character_id, character_data = test_character
    
    # Initialize services
    data_service = CharacterDataService()
    char_service = CharacterService(character_id, data_service=data_service)
    
    # Initial state
    assert character_data.equipment.gold == 100
    
    # Add gold
    char_service.add_gold(50)
    
    # Verify in-memory state
    updated_character = char_service.get_character()
    assert updated_character.equipment.gold == 150
    
    # Verify persistence
    saved_data = load_character_from_file(temp_data_dir, character_id)
    assert saved_data["equipment"]["gold"] == 150


def test_add_xp_with_level_up(temp_data_dir, test_character):
    """Test adding enough XP to trigger level up"""
    character_id, character_data = test_character
    
    # Initialize services
    data_service = CharacterDataService()
    char_service = CharacterService(character_id, data_service=data_service)
    
    # Add enough XP for level 2 (threshold is level * 1000, so 1 * 1000 = 1000 XP)
    char_service.apply_xp(1000)
    
    # Verify level up
    updated_character = char_service.get_character()
    assert updated_character.experience_points == 1000
    assert updated_character.level == 2
    
    # Verify persistence
    saved_data = load_character_from_file(temp_data_dir, character_id)
    assert saved_data["level"] == 2
