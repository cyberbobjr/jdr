import pytest
from back.services.character_service import CharacterService
from back.models.schema import Character

def test_get_all_characters(isolated_data_dir):
    characters = CharacterService.get_all_characters()
    assert isinstance(characters, list)
    assert len(characters) > 0
    assert isinstance(characters[0], Character)
    assert hasattr(characters[0], "equipment")
    assert hasattr(characters[0], "spells")
    assert hasattr(characters[0], "equipment_summary")
    assert hasattr(characters[0], "culture_bonuses")
