"""
DEPRECATED: These tests are obsolete. They were written for the old API that accepted dict.
The new API only accepts Character objects.
See test_character_persistence_serialization.py for the new tests.
"""

import pytest
from unittest.mock import patch

# Keep minimal test structure for backwards compatibility
@pytest.fixture
def temp_characters_dir(tmp_path):
    """Create a temporary directory for character data and patch the service."""
    d = tmp_path / "characters"
    d.mkdir()
    with patch('back.services.character_persistence_service.CHARACTERS_DIR', str(d)):
        yield str(d)

@pytest.mark.skip(reason="Obsolete test - save_character_data now only accepts Character objects. See test_character_persistence_serialization.py")
def test_save_character_data_success(temp_characters_dir):
    pass

@pytest.mark.skip(reason="Obsolete test - save_character_data now only accepts Character objects. See test_character_persistence_serialization.py")
def test_save_character_data_overwrite(temp_characters_dir):
    pass

@pytest.mark.skip(reason="Obsolete test - save_character_data now only accepts Character objects. See test_character_persistence_serialization.py")
def test_save_character_data_serialization(temp_characters_dir):
    pass

@pytest.mark.skip(reason="Obsolete test - save_character_data now only accepts Character objects. See test_character_persistence_serialization.py")
def test_save_character_data_creates_directory(tmp_path):
    pass

@pytest.mark.skip(reason="Obsolete test - save_character_data now only accepts Character objects. See test_character_persistence_serialization.py")
def test_save_character_data_invalid_id():
    pass

@pytest.mark.skip(reason="Obsolete test - save_character_data now only accepts Character objects. See test_character_persistence_serialization.py")
def test_save_character_data_non_serializable(temp_characters_dir):
    pass
