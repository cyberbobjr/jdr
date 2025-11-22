from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
from back.app import app
from back.models.domain.character import Character, Stats, Skills, CombatStats, CharacterStatus
from back.models.schema import ActiveSessionsResponse

client = TestClient(app)

def test_list_active_sessions_success():
    """
    Test successful listing of active game sessions.
    """
    mock_session_id = uuid4()
    mock_character_id = uuid4()

    mock_sessions = [
        {
            "session_id": mock_session_id,
            "scenario_name": "Test Scenario",
            "character_id": mock_character_id,
        }
    ]

    mock_stats = Stats(strength=10, constitution=10, agility=10, intelligence=10, wisdom=10, charisma=10)
    mock_skills = Skills()
    mock_combat_stats = CombatStats(max_hit_points=100, current_hit_points=100)

    mock_character = Character(
        id=mock_character_id,
        name="Test Character",
        race="Human",
        culture="Gondor",
        stats=mock_stats,
        skills=mock_skills,
        combat_stats=mock_combat_stats,
    )

    with patch('back.routers.gamesession.GameSessionService.list_all_sessions', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_sessions
        with patch('back.routers.gamesession.CharacterDataService') as MockDataService:
            MockDataService.return_value.load_character.return_value = mock_character
            response = client.get("/api/gamesession/sessions")
    
    assert response.status_code == 200
    active_sessions_response = ActiveSessionsResponse.model_validate(response.json())
    assert len(active_sessions_response.sessions) == 1
    session_info = active_sessions_response.sessions[0]
    assert session_info.session_id == str(mock_session_id)
    assert session_info.character_id == str(mock_character_id)
    assert session_info.character_name == "Test Character"

def test_list_active_sessions_empty():
    """
    Test listing active sessions when none exist.
    """
    with patch('back.routers.gamesession.GameSessionService.list_all_sessions', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = []
        response = client.get("/api/gamesession/sessions")

        assert response.status_code == 200
        active_sessions_response = ActiveSessionsResponse.model_validate(response.json())
        assert len(active_sessions_response.sessions) == 0

def test_list_active_sessions_character_not_found():
    """
    Test listing active sessions when a character is not found.
    """
    mock_session_id = uuid4()
    mock_character_id = uuid4()

    mock_sessions = [
        {
            "session_id": mock_session_id,
            "scenario_name": "Test Scenario",
            "character_id": mock_character_id,
        }
    ]

    with patch('back.routers.gamesession.GameSessionService.list_all_sessions', new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_sessions
        with patch('back.routers.gamesession.CharacterDataService') as MockDataService:
            MockDataService.return_value.load_character.side_effect = FileNotFoundError
            response = client.get("/api/gamesession/sessions")

    assert response.status_code == 200
    active_sessions_response = ActiveSessionsResponse.model_validate(response.json())
    assert len(active_sessions_response.sessions) == 1
    session_info = active_sessions_response.sessions[0]
    assert session_info.character_name == "Unknown"

def test_start_scenario_success():
    """
    Test successfully starting a new scenario.
    """
    from back.graph.dto.session import GameState, DispatchResult
    mock_session_id = uuid4()
    mock_character_id = uuid4()
    mock_scenario_name = "Test Scenario"
    mock_llm_response = "Initial narration."

    start_scenario_response = {
        "session_id": str(mock_session_id),
        "scenario_name": mock_scenario_name,
        "character_id": str(mock_character_id),
    }

    mock_game_state = GameState(
        session_mode="narrative",
        narrative_history_id="default",
        combat_history_id="default"
    )
    
    # Expected messages should match ConversationMessage structure or be compatible
    # The router returns ConversationMessage objects now.
    # But the test checks response.json() which is a list of dicts.
    # The router constructs PlayScenarioResponse(response=result.output.all_messages, ...)
    # result.output.all_messages are ModelMessage objects.
    # Pydantic serializes them.
    # We need to ensure our mock returns something that can be serialized.
    
    # Mock ModelMessage
    mock_message = MagicMock()
    mock_message.content = mock_llm_response
    mock_message.kind = "response" # or whatever ModelMessage uses
    # Actually, let's use a dict that matches the structure if we can, or just check basic fields.
    # But wait, the router uses `result.output.all_messages`.
    # If we mock `mock_dispatch_result.all_messages` as a list of dicts, Pydantic might complain if it expects ModelMessage objects?
    # No, Pydantic validates the *output* of the endpoint against the response model.
    # The endpoint returns `PlayScenarioResponse`.
    # `PlayScenarioResponse` expects `List[ConversationMessage]`.
    # `ConversationMessage` is a Pydantic model.
    # If `all_messages` is a list of dicts, Pydantic will try to parse them into `ConversationMessage`.
    
    expected_message_dict = {
        "parts": [{"content": mock_llm_response, "part_kind": "text", "timestamp": "2024-01-01T00:00:00Z"}],
        "kind": "response",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    mock_dispatch_result = DispatchResult(all_messages=[expected_message_dict], new_messages=[expected_message_dict])

    with patch('back.routers.gamesession.CharacterDataService') as MockDataService:
        mock_data_instance = MockDataService.return_value
        mock_char = MagicMock()
        mock_char.status = CharacterStatus.ACTIVE
        mock_data_instance.load_character.return_value = mock_char
        
        with patch('back.routers.gamesession.GameSessionService') as MockSessionService:
            mock_service_instance = MagicMock()
            
            # Configure the static method on the mock class
            MockSessionService.start_scenario = AsyncMock(return_value=start_scenario_response)
            MockSessionService.load = AsyncMock(return_value=mock_service_instance)
            
            mock_service_instance.load_game_state = AsyncMock(return_value=mock_game_state)
            mock_service_instance.update_game_state = AsyncMock()
            
            # MockSessionService is the class. 
            # In the router: await GameSessionService.start_scenario(...)
            # await GameSessionService.load(...)
            
            with patch('back.routers.gamesession.session_graph.run', new_callable=AsyncMock) as mock_run:
                mock_run_result = MagicMock()
                mock_run_result.output = mock_dispatch_result
                mock_run.return_value = mock_run_result

                request_data = {
                    "scenario_name": mock_scenario_name,
                    "character_id": str(mock_character_id)
                }
                response = client.post("/api/gamesession/play", json=request_data)

                assert response.status_code == 200
                response_data = response.json()
                assert "response" in response_data
                assert "session_id" in response_data
                assert response_data["session_id"] == str(mock_session_id)
                # Check content of response
                assert len(response_data["response"]) == 1
                assert response_data["response"][0]["parts"][0]["content"] == mock_llm_response


