"""
Unit tests for GameSessionService.
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from back.services.game_session_service import GameSessionService
from back.models.domain.character import Character


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

        with pytest.raises(FileNotFoundError, match="does not exist"):
            GameSessionService.start_scenario(scenario_name, character_id)

    def test_get_session_info_success(self):
        """
        Test retrieving session info successfully.
        """
        scenario_name = "Les_Pierres_du_Passe.md"
        character_id = uuid4()
        session_result = GameSessionService.start_scenario(scenario_name, character_id)
        session_id = session_result["session_id"]

        info = GameSessionService.get_session_info(session_id)

        assert info["character_id"] == str(character_id)
        assert info["scenario_name"] == scenario_name

    def test_get_session_info_invalid_session(self):
        """
        Test retrieving info for non-existent session raises FileNotFoundError.
        """
        with pytest.raises(FileNotFoundError, match="does not exist"):
            GameSessionService.get_session_info("invalid-session-id")

    def test_check_existing_session_true(self):
        """
        Test checking existing session returns True.
        """
        scenario_name = "Les_Pierres_du_Passe.md"
        character_id = uuid4()
        GameSessionService.start_scenario(scenario_name, character_id)

        exists = GameSessionService.check_existing_session(scenario_name, str(character_id))
        assert exists is True

    def test_check_existing_session_false(self):
        """
        Test checking non-existing session returns False.
        """
        scenario_name = "Les_Pierres_du_Passe.md"
        character_id = str(uuid4())

        exists = GameSessionService.check_existing_session(scenario_name, character_id)
        assert exists is False

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

        business_service = Mock()
        business_service.apply_xp.return_value = mock_character
        business_service.add_gold.return_value = mock_character
        business_service.take_damage.return_value = mock_character

        equipment_service = Mock()
        equipment_service.add_item.return_value = mock_character
        equipment_service.remove_item.return_value = mock_character
        equipment_service.buy_equipment.return_value = mock_character
        equipment_service.sell_equipment.return_value = mock_character

        return {
            'data_service': data_service,
            'business_service': business_service,
            'equipment_service': equipment_service
        }

    def _setup_service(self, service, mock_services):
        """Helper to setup service with mocked dependencies."""
        service.data_service = mock_services['data_service']
        service.business_service = mock_services['business_service']
        service.equipment_service = mock_services['equipment_service']
        service.character_data = mock_services['data_service'].load_character.return_value
        return service

    @patch('back.services.game_session_service.CharacterDataService')
    @patch('back.services.game_session_service.CharacterBusinessService')
    @patch('back.services.game_session_service.EquipmentService')
    def test_apply_xp(self, mock_equipment_service_cls, mock_business_service_cls, mock_data_service_cls, mock_services):
        """Test applying XP to character."""
        # Setup mocks
        mock_data_service_cls.return_value = mock_services['data_service']
        mock_business_service_cls.return_value = mock_services['business_service']
        mock_equipment_service_cls.return_value = mock_services['equipment_service']

        # Create session service with mocked session
        with patch.object(GameSessionService, '_load_session_data', return_value=True), \
             patch.object(GameSessionService, '_initialize_services'):
            service = GameSessionService("test-session")
            service = self._setup_service(service, mock_services)

            result = service.apply_xp(100)

            mock_services['business_service'].apply_xp.assert_called_once_with(service.character_data, 100)
            assert result == mock_services['data_service'].load_character.return_value

    @patch('back.services.game_session_service.CharacterDataService')
    @patch('back.services.game_session_service.CharacterBusinessService')
    @patch('back.services.game_session_service.EquipmentService')
    def test_add_gold(self, mock_equipment_service_cls, mock_business_service_cls, mock_data_service_cls, mock_services):
        """Test adding gold to character."""
        mock_data_service_cls.return_value = mock_services['data_service']
        mock_business_service_cls.return_value = mock_services['business_service']
        mock_equipment_service_cls.return_value = mock_services['equipment_service']

        with patch.object(GameSessionService, '_load_session_data', return_value=True), \
             patch.object(GameSessionService, '_initialize_services'):
            service = GameSessionService("test-session")
            service = self._setup_service(service, mock_services)

            result = service.add_gold(25.0)

            mock_services['business_service'].add_gold.assert_called_once_with(service.character_data, 25.0)
            assert result == mock_services['data_service'].load_character.return_value

    @patch('back.services.game_session_service.CharacterDataService')
    @patch('back.services.game_session_service.CharacterBusinessService')
    @patch('back.services.game_session_service.EquipmentService')
    def test_take_damage(self, mock_equipment_service_cls, mock_business_service_cls, mock_data_service_cls, mock_services):
        """Test applying damage to character."""
        mock_data_service_cls.return_value = mock_services['data_service']
        mock_business_service_cls.return_value = mock_services['business_service']
        mock_equipment_service_cls.return_value = mock_services['equipment_service']

        with patch.object(GameSessionService, '_load_session_data', return_value=True):
            service = GameSessionService("test-session")
            service.character_data = mock_services['data_service'].load_character.return_value

            result = service.take_damage(20, "combat")

            mock_services['business_service'].take_damage.assert_called_once_with(service.character_data, 20, "combat")
            assert result == mock_services['data_service'].load_character.return_value

    @patch('back.services.game_session_service.CharacterDataService')
    @patch('back.services.game_session_service.CharacterBusinessService')
    @patch('back.services.game_session_service.EquipmentService')
    def test_add_item(self, mock_equipment_service_cls, mock_business_service_cls, mock_data_service_cls, mock_services):
        """Test adding item to character inventory."""
        mock_data_service_cls.return_value = mock_services['data_service']
        mock_business_service_cls.return_value = mock_services['business_service']
        mock_equipment_service_cls.return_value = mock_services['equipment_service']

        with patch.object(GameSessionService, '_load_session_data', return_value=True):
            service = GameSessionService("test-session")
            service.character_data = mock_services['data_service'].load_character.return_value

            result = service.add_item("sword", 2)

            mock_services['equipment_service'].add_item.assert_called_once_with(service.character_data, "sword", 2)
            assert result == mock_services['data_service'].load_character.return_value

    @patch('back.services.game_session_service.CharacterDataService')
    @patch('back.services.game_session_service.CharacterBusinessService')
    @patch('back.services.game_session_service.EquipmentService')
    def test_remove_item(self, mock_equipment_service_cls, mock_business_service_cls, mock_data_service_cls, mock_services):
        """Test removing item from character inventory."""
        mock_data_service_cls.return_value = mock_services['data_service']
        mock_business_service_cls.return_value = mock_services['business_service']
        mock_equipment_service_cls.return_value = mock_services['equipment_service']

        with patch.object(GameSessionService, '_load_session_data', return_value=True):
            service = GameSessionService("test-session")
            service.character_data = mock_services['data_service'].load_character.return_value

            result = service.remove_item("sword", 1)

            mock_services['equipment_service'].remove_item.assert_called_once_with(service.character_data, "sword", 1)
            assert result == mock_services['data_service'].load_character.return_value

    @patch('back.services.game_session_service.CharacterDataService')
    @patch('back.services.game_session_service.CharacterBusinessService')
    @patch('back.services.game_session_service.EquipmentService')
    def test_buy_equipment(self, mock_equipment_service_cls, mock_business_service_cls, mock_data_service_cls, mock_services):
        """Test buying equipment."""
        mock_data_service_cls.return_value = mock_services['data_service']
        mock_business_service_cls.return_value = mock_services['business_service']
        mock_equipment_service_cls.return_value = mock_services['equipment_service']

        with patch.object(GameSessionService, '_load_session_data', return_value=True):
            service = GameSessionService("test-session")
            service.character_data = mock_services['data_service'].load_character.return_value

            result = service.buy_equipment("sword")

            mock_services['equipment_service'].buy_equipment.assert_called_once_with(service.character_data, "sword")
            assert result == mock_services['data_service'].load_character.return_value

    @patch('back.services.game_session_service.CharacterDataService')
    @patch('back.services.game_session_service.CharacterBusinessService')
    @patch('back.services.game_session_service.EquipmentService')
    def test_sell_equipment(self, mock_equipment_service_cls, mock_business_service_cls, mock_data_service_cls, mock_services):
        """Test selling equipment."""
        mock_data_service_cls.return_value = mock_services['data_service']
        mock_business_service_cls.return_value = mock_services['business_service']
        mock_equipment_service_cls.return_value = mock_services['equipment_service']

        with patch.object(GameSessionService, '_load_session_data', return_value=True):
            service = GameSessionService("test-session")
            service.character_data = mock_services['data_service'].load_character.return_value

            result = service.sell_equipment("sword")

            mock_services['equipment_service'].sell_equipment.assert_called_once_with(service.character_data, "sword")
            assert result == mock_services['data_service'].load_character.return_value

    @patch('back.services.game_session_service.CharacterDataService')
    @patch('back.services.game_session_service.CharacterBusinessService')
    @patch('back.services.game_session_service.EquipmentService')
    @pytest.mark.asyncio
    async def test_save_history(self, mock_equipment_service_cls, mock_business_service_cls, mock_data_service_cls, mock_services):
        """Test saving history."""
        from pydantic_ai.messages import ModelMessagesTypeAdapter

        mock_data_service_cls.return_value = mock_services['data_service']
        mock_business_service_cls.return_value = mock_services['business_service']
        mock_equipment_service_cls.return_value = mock_services['equipment_service']

        # Create sample messages
        sample_data = [{"kind": "request", "parts": [{"content": "test", "part_kind": "user-prompt"}]}]
        messages = ModelMessagesTypeAdapter.validate_python(sample_data)

        with patch.object(GameSessionService, '_load_session_data', return_value=True):
            service = GameSessionService("test-session")

            # Mock the PydanticJsonlStore
            with patch('back.services.game_session_service.PydanticJsonlStore') as mock_store_cls:
                mock_store = Mock()
                mock_store_cls.return_value = mock_store

                await service.save_history("narrative", messages)

                mock_store_cls.assert_called_once()
                mock_store.save_pydantic_history.assert_called_once_with(messages)

    @patch('back.services.game_session_service.CharacterDataService')
    @patch('back.services.game_session_service.CharacterBusinessService')
    @patch('back.services.game_session_service.EquipmentService')
    @pytest.mark.asyncio
    async def test_load_history_raw_json(self, mock_equipment_service_cls, mock_business_service_cls, mock_data_service_cls, mock_services):
        """Test loading raw JSON history."""
        mock_data_service_cls.return_value = mock_services['data_service']
        mock_business_service_cls.return_value = mock_services['business_service']
        mock_equipment_service_cls.return_value = mock_services['equipment_service']

        with patch.object(GameSessionService, '_load_session_data', return_value=True):
            service = GameSessionService("test-session")

            # Mock the PydanticJsonlStore
            with patch('back.services.game_session_service.PydanticJsonlStore') as mock_store_cls:
                mock_store = Mock()
                mock_store.load_raw_json_history.return_value = [{"kind": "request", "parts": []}]
                mock_store_cls.return_value = mock_store

                result = await service.load_history_raw_json("narrative")

                mock_store_cls.assert_called_once()
                mock_store.load_raw_json_history.assert_called_once_with()
                assert result == [{"kind": "request", "parts": []}]
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

        with pytest.raises(FileNotFoundError, match="does not exist"):
            GameSessionService.start_scenario(scenario_name, character_id)

    def test_get_session_info_success(self):
        """
        Test retrieving session info successfully.
        """
        scenario_name = "Les_Pierres_du_Passe.md"
        character_id = uuid4()
        session_result = GameSessionService.start_scenario(scenario_name, character_id)
        session_id = session_result["session_id"]

        info = GameSessionService.get_session_info(session_id)

        assert info["character_id"] == str(character_id)
        assert info["scenario_name"] == scenario_name

    def test_get_session_info_invalid_session(self):
        """
        Test retrieving info for non-existent session raises FileNotFoundError.
        """
        with pytest.raises(FileNotFoundError, match="does not exist"):
            GameSessionService.get_session_info("invalid-session-id")

    def test_check_existing_session_true(self):
        """
        Test checking existing session returns True.
        """
        scenario_name = "Les_Pierres_du_Passe.md"
        character_id = uuid4()
        GameSessionService.start_scenario(scenario_name, character_id)

        exists = GameSessionService.check_existing_session(scenario_name, str(character_id))
        assert exists is True

    def test_check_existing_session_false(self):
        """
        Test checking non-existing session returns False.
        """
        scenario_name = "Les_Pierres_du_Passe.md"
        character_id = str(uuid4())

        exists = GameSessionService.check_existing_session(scenario_name, character_id)
        assert exists is False

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