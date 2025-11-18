"""
Unit tests for GameSessionService.
"""

import pytest
from uuid import uuid4
from back.services.game_session_service import GameSessionService


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