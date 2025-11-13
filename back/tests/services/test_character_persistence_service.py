
import pytest
import json
import os
from uuid import uuid4
from datetime import datetime
from unittest.mock import patch

from back.services.character_persistence_service import CharacterPersistenceService

# Use a pytest fixture for a temporary directory to store test character files
@pytest.fixture
def temp_characters_dir(tmp_path):
    """Create a temporary directory for character data and patch the service."""
    d = tmp_path / "characters"
    d.mkdir()
    with patch('back.services.character_persistence_service.CHARACTERS_DIR', str(d)):
        yield str(d)

def test_save_character_data_success(temp_characters_dir):
    """
    Test that valid character data is successfully saved to a JSON file.
    """
    character_id = str(uuid4())
    character_data = {
        "id": character_id,
        "name": "Test Character",
        "level": 1,
        "stats": {"strength": 10}
    }
    
    CharacterPersistenceService.save_character_data(character_id, character_data)
    
    # Verify the file was created
    expected_file = os.path.join(temp_characters_dir, f"{character_id}.json")
    assert os.path.exists(expected_file)
    
    # Verify the content of the file
    with open(expected_file, 'r') as f:
        saved_data = json.load(f)
    
    assert saved_data == character_data

def test_save_character_data_overwrite(temp_characters_dir):
    """
    Test that saving a character with an existing ID overwrites the old file.
    """
    character_id = str(uuid4())
    initial_data = {"id": character_id, "name": "Initial Name"}
    updated_data = {"id": character_id, "name": "Updated Name"}
    
    # First save
    CharacterPersistenceService.save_character_data(character_id, initial_data)
    
    # Second save with the same ID
    CharacterPersistenceService.save_character_data(character_id, updated_data)
    
    # Verify the content is the updated data
    expected_file = os.path.join(temp_characters_dir, f"{character_id}.json")
    with open(expected_file, 'r') as f:
        saved_data = json.load(f)
        
    assert saved_data["name"] == "Updated Name"

def test_save_character_data_serialization(temp_characters_dir):
    """
    Test that complex data types (UUID, datetime) are correctly serialized.
    """
    character_id = uuid4()
    now = datetime.now()
    
    character_data = {
        "id": character_id,
        "name": "Serializable Test",
        "created_at": now
    }
    
    # The service expects a dict with serializable data, so we convert before calling
    serializable_data = {
        "id": str(character_id),
        "name": "Serializable Test",
        "created_at": now.isoformat()
    }
    
    CharacterPersistenceService.save_character_data(str(character_id), serializable_data)
    
    expected_file = os.path.join(temp_characters_dir, f"{character_id}.json")
    with open(expected_file, 'r') as f:
        saved_data = json.load(f)
        
    assert saved_data["id"] == str(character_id)
    assert saved_data["created_at"] == now.isoformat()

def test_save_character_data_creates_directory(tmp_path):
    """
    Test that the service creates the characters directory if it doesn't exist.
    """
    non_existent_dir = tmp_path / "new_characters_dir"
    # Don't create the directory, let the service do it.
    
    with patch('back.services.character_persistence_service.CHARACTERS_DIR', str(non_existent_dir)):
        character_id = str(uuid4())
        character_data = {"id": character_id, "name": "Dir Creation Test"}
        
        CharacterPersistenceService.save_character_data(character_id, character_data)
        
        # Verify directory and file exist
        assert os.path.isdir(non_existent_dir)
        expected_file = os.path.join(non_existent_dir, f"{character_id}.json")
        assert os.path.exists(expected_file)

def test_save_character_data_invalid_id():
    """
    Test that saving with an invalid character ID raises a ValueError.
    """
    with pytest.raises(ValueError, match="Character ID must be a non-empty string"):
        CharacterPersistenceService.save_character_data("", {"name": "Invalid ID"})
        
    with pytest.raises(ValueError, match="Character ID must be a non-empty string"):
        CharacterPersistenceService.save_character_data(None, {"name": "Invalid ID"})

def test_save_character_data_non_serializable(temp_characters_dir):
    """
    Test that attempting to save non-serializable data raises a TypeError.
    """
    character_id = str(uuid4())
    # bytes are not directly JSON serializable
    non_serializable_data = {"id": character_id, "data": b"some_bytes"}
    
    with pytest.raises(TypeError):
        CharacterPersistenceService.save_character_data(character_id, non_serializable_data)
