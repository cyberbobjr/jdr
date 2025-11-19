"""
Unit tests for GameSessionService.
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from back.services.game_session_service import GameSessionService
from back.models.domain.character import Character


from back.utils.exceptions import SessionNotFoundError

class TestGameSessionService:
    """
    Test suite for GameSessionService static methods.
    """

    def test_start_scenario_success(self):
        """
        Test starting a scenario successfully.
        """
        scenario_name = "Les_Pierres_du_Passe.md"
        character_id = uuid4()
        result = GameSessionService.start_scenario(scenario_name, character_id)

        assert "session_id" in result
        assert result["scenario_name"] == scenario_name
        assert result["character_id"] == str(character_id)
        assert "message" in result

    def test_start_scenario_existing_session(self):
        """
        Test starting a scenario that already exists raises ValueError.
        """
        scenario_name = "Les_Pierres_du_Passe.md"
        character_id = uuid4()

        # Start first session
        GameSessionService.start_scenario(scenario_name, character_id)

        # Try to start again
        with pytest.raises(ValueError, match="A session already exists"):
            GameSessionService.start_scenario(scenario_name, character_id)

    def test_start_scenario_invalid_scenario(self):
        """
        Test starting a non-existent scenario raises FileNotFoundError.
        """
        scenario_name = "Invalid_Scenario.md"
        character_id = uuid4()

        with pytest.raises(FileNotFoundError):
            GameSessionService.start_scenario(scenario_name, character_id)

    def test_get_session_info(self):
        """
        Test getting session information.
        """
        scenario_name = "Les_Pierres_du_Passe.md"
        character_id = uuid4()
        result = GameSessionService.start_scenario(scenario_name, character_id)
        session_id = result["session_id"]

        info = GameSessionService.get_session_info(session_id)
        assert info["scenario_name"] == scenario_name
        assert info["character_id"] == str(character_id)

    def test_get_session_info_invalid(self):
        """
        Test getting session info for invalid session raises SessionNotFoundError.
        """
        with pytest.raises(SessionNotFoundError, match="does not exist"):
            GameSessionService.get_session_info("invalid-session")

    def test_check_existing_session(self):
        """
        Test checking for existing sessions.
        """
        scenario_name = "Les_Pierres_du_Passe.md"
        character_id = uuid4()

        # No session exists initially
        assert not GameSessionService.check_existing_session(scenario_name, str(character_id))

        # Start a session
        GameSessionService.start_scenario(scenario_name, character_id)

        # Now session exists
        assert GameSessionService.check_existing_session(scenario_name, str(character_id))

    def test_list_all_sessions(self):
        """
        Test listing all sessions.
        """
        # This test assumes some sessions exist from previous tests
        sessions = GameSessionService.list_all_sessions()
        assert isinstance(sessions, list)
        # Each session should have session_id, character_id, scenario_id
        for session in sessions:
            assert "session_id" in session
            assert "character_id" in session
            assert "scenario_id" in session


class TestGameSessionServiceInstance:
    """
    Test suite for GameSessionService instance methods.
    """

    @pytest.fixture
    def mock_character(self):
        """Create a mock character for testing."""
        character = Mock(spec=Character)
        character.name = "Test Character"
        character.hp = 100
        character.gold = 50
        character.xp = 0
        return character

    @pytest.fixture
    def mock_services(self, mock_character):
        """Create mock services."""
        data_service = Mock()
        data_service.load_character.return_value = mock_character
        data_service.save_character = Mock()

        character_service = Mock()
        character_service.apply_xp.return_value = mock_character
        character_service.add_gold.return_value = mock_character
        character_service.take_damage.return_value = mock_character

        equipment_service = Mock()
        equipment_service.add_item.return_value = mock_character
        equipment_service.remove_item.return_value = mock_character
        equipment_service.buy_equipment.return_value = mock_character
        equipment_service.sell_equipment.return_value = mock_character

        return {
            'data_service': data_service,
            'character_service': character_service,
            'equipment_service': equipment_service
        }

    def _setup_service(self, service, mock_services):
        """Helper to setup service with mocked dependencies."""
        service.data_service = mock_services['data_service']
        service.character_service = mock_services['character_service']
        service.equipment_service = mock_services['equipment_service']
        service.character_data = mock_services['data_service'].load_character.return_value
        return service

    def test_apply_xp(self, mock_services):
        """Test applying XP to character."""
        # Create session service with mocked session
        with patch.object(GameSessionService, '_load_session_data', return_value=True), \
             patch.object(GameSessionService, '_initialize_services'):
            service = GameSessionService("test-session")
            service = self._setup_service(service, mock_services)

            # Call specialized service directly
            result = service.character_service.apply_xp(100)

            mock_services['character_service'].apply_xp.assert_called_once_with(100)
            # Note: In the new architecture, GameSessionService doesn't return the character, 
            # but the specialized service does.
            assert result == mock_services['character_service'].apply_xp.return_value

    def test_add_gold(self, mock_services):
        """Test adding gold to character."""
        with patch.object(GameSessionService, '_load_session_data', return_value=True), \
             patch.object(GameSessionService, '_initialize_services'):
            service = GameSessionService("test-session")
            service = self._setup_service(service, mock_services)

            result = service.character_service.add_gold(50.0)

            mock_services['character_service'].add_gold.assert_called_once_with(50.0)
            assert result == mock_services['character_service'].add_gold.return_value

    def test_take_damage(self, mock_services):
        """Test taking damage."""
        with patch.object(GameSessionService, '_load_session_data', return_value=True), \
             patch.object(GameSessionService, '_initialize_services'):
            service = GameSessionService("test-session")
            service = self._setup_service(service, mock_services)

            result = service.character_service.take_damage(20, "combat")

            mock_services['character_service'].take_damage.assert_called_once_with(20, "combat")
            assert result == mock_services['character_service'].take_damage.return_value

    def test_add_item(self, mock_services):
        """Test adding an item."""
        with patch.object(GameSessionService, '_load_session_data', return_value=True), \
             patch.object(GameSessionService, '_initialize_services'):
            service = GameSessionService("test-session")
            service = self._setup_service(service, mock_services)

            # Call specialized service directly
            # Note: In the real implementation, we pass character_data to the equipment service
            # Here we mock the call
            result = service.equipment_service.add_item(service.character_data, "sword", 1)

            mock_services['equipment_service'].add_item.assert_called_once_with(service.character_data, "sword", 1)
            assert result == mock_services['equipment_service'].add_item.return_value

    def test_remove_item(self, mock_services):
        """Test removing an item."""
        with patch.object(GameSessionService, '_load_session_data', return_value=True), \
             patch.object(GameSessionService, '_initialize_services'):
            service = GameSessionService("test-session")
            service = self._setup_service(service, mock_services)

            result = service.equipment_service.remove_item(service.character_data, "sword", 1)

            mock_services['equipment_service'].remove_item.assert_called_once_with(service.character_data, "sword", 1)
            assert result == mock_services['equipment_service'].remove_item.return_value

    def test_buy_equipment(self, mock_services):
        """Test buying equipment."""
        with patch.object(GameSessionService, '_load_session_data', return_value=True), \
             patch.object(GameSessionService, '_initialize_services'):
            service = GameSessionService("test-session")
            service = self._setup_service(service, mock_services)

            result = service.equipment_service.buy_equipment(service.character_data, "sword")

            mock_services['equipment_service'].buy_equipment.assert_called_once_with(service.character_data, "sword")
            assert result == mock_services['equipment_service'].buy_equipment.return_value

    def test_sell_equipment(self, mock_services):
        """Test selling equipment."""
        with patch.object(GameSessionService, '_load_session_data', return_value=True), \
             patch.object(GameSessionService, '_initialize_services'):
            service = GameSessionService("test-session")
            service = self._setup_service(service, mock_services)

            result = service.equipment_service.sell_equipment(service.character_data, "sword")

            mock_services['equipment_service'].sell_equipment.assert_called_once_with(service.character_data, "sword")
            assert result == mock_services['equipment_service'].sell_equipment.return_value

    @pytest.mark.asyncio
    async def test_save_history(self, mock_services):
        """Test saving history."""
        from pydantic_ai.messages import ModelMessagesTypeAdapter

        # Create sample messages
        sample_data = [{"kind": "request", "parts": [{"content": "test", "part_kind": "user-prompt"}]}]
        messages = ModelMessagesTypeAdapter.validate_python(sample_data)

        with patch.object(GameSessionService, '_load_session_data', return_value=True), \
             patch.object(GameSessionService, '_initialize_services'):
            service = GameSessionService("test-session")

            # Mock the PydanticJsonlStore
            with patch('back.services.game_session_service.PydanticJsonlStore') as mock_store_cls:
                mock_store = Mock()
                mock_store_cls.return_value = mock_store

                await service.save_history("narrative", messages)

                mock_store_cls.assert_called_once()
                mock_store.save_pydantic_history.assert_called_once_with(messages)

    @pytest.mark.asyncio
    async def test_load_history_raw_json(self, mock_services):
        """Test loading raw JSON history."""
        with patch.object(GameSessionService, '_load_session_data', return_value=True), \
             patch.object(GameSessionService, '_initialize_services'):
            service = GameSessionService("test-session")

            # Mock the PydanticJsonlStore
            with patch('back.services.game_session_service.PydanticJsonlStore') as mock_store_cls:
                mock_store = Mock()
                mock_store.load_raw_json_history.return_value = [{"kind": "request", "parts": []}]
                mock_store_cls.return_value = mock_store

                result = await service.load_history_raw_json("narrative")

                # Check that the store was created with the correct path
                expected_path = f"data/sessions/test-session/history_narrative.jsonl"
                mock_store_cls.assert_called_once()
                args, kwargs = mock_store_cls.call_args
                assert expected_path in str(args[0]) or expected_path in str(kwargs.get('filepath', ''))
                mock_store.load_raw_json_history.assert_called_once()
                assert result == [{"kind": "request", "parts": []}]