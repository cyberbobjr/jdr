import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from back.services.game_session_service import GameSessionService
from back.models.enums import CharacterStatus

@pytest.fixture
def mock_character_service():
    with patch('back.services.game_session_service.CharacterService') as MockCharService:
        yield MockCharService

@pytest.fixture
def mock_session_setup():
    with patch('back.services.game_session_service.pathlib.Path') as MockPath, \
         patch('back.services.game_session_service.get_data_dir', return_value="/tmp/data"):
        
        # Setup mock paths
        mock_scenarios_dir = MockPath.return_value / "scenarios"
        mock_sessions_dir = MockPath.return_value / "sessions"
        
        # Setup scenario existence check
        mock_scenario_path = mock_scenarios_dir / "test_scenario.md"
        mock_scenario_path.exists.return_value = True
        
        yield mock_sessions_dir

def test_start_scenario_sets_in_game_status(mock_character_service, mock_session_setup):
    # Arrange
    scenario_name = "test_scenario.md"
    character_id = uuid4()
    
    # Mock CharacterService instance
    mock_char_service_instance = mock_character_service.return_value
    mock_char_service_instance.character_data = MagicMock()
    
    # Mock check_existing_session to return False
    with patch.object(GameSessionService, 'check_existing_session', return_value=False):
        # Act
        GameSessionService.start_scenario(scenario_name, character_id)
        
        # Assert
        # Verify CharacterService was initialized with correct ID
        mock_character_service.assert_called_with(str(character_id))
        
        # Verify status was updated to IN_GAME
        assert mock_char_service_instance.character_data.status == CharacterStatus.IN_GAME
        
        # Verify save_character was called
        mock_char_service_instance.save_character.assert_called_once()
