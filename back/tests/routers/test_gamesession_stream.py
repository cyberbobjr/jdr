from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from back.app import app
from back.utils.exceptions import SessionNotFoundError

client = TestClient(app)

def mock_stream_and_final_response(chunks, final_messages):
    """A helper to mock the streaming behavior and the final response."""
    async def stream_iterator():
        for chunk in chunks:
            yield chunk

    stream_mock = MagicMock()
    stream_mock.stream = stream_iterator
    stream_mock.get_final_response = AsyncMock(return_value=MagicMock(all_messages=MagicMock(return_value=final_messages)))

    # This makes the object an async context manager
    async_context_manager = AsyncMock()
    async_context_manager.__aenter__.return_value = stream_mock
    return async_context_manager

def test_play_stream_success():
    """
    Test successful streaming of a game session response with the graph system.
    """
    session_id = uuid4()
    character_id = uuid4()
    scenario_name = "TestStreamScenario"
    user_message = "I inspect the area."
    response_text = "The air is cold. You see a strange symbol on the wall."
    
    from back.graph.dto.session import GameState, DispatchResult
    from datetime import datetime
    
    mock_game_state = GameState(
        session_mode="narrative",
        narrative_history_id="default",
        combat_history_id="default"
    )
    
    # Expected messages from the graph
    expected_messages = [
        {
            "content": response_text,
            "timestamp": datetime.now().isoformat(),
            "part_kind": "text"
        }
    ]
    
    mock_result = DispatchResult(all_messages=expected_messages, new_messages=expected_messages)

    with patch('back.routers.gamesession.GameSessionService') as MockSessionService:
        mock_service_instance = AsyncMock()
        mock_service_instance.session_id = str(session_id)
        mock_service_instance.load_game_state = AsyncMock(return_value=mock_game_state)
        mock_service_instance.update_game_state = AsyncMock()
        mock_service_instance.load_history = AsyncMock(return_value=[])
        mock_service_instance.save_history = AsyncMock()
        mock_service_instance.build_narrative_system_prompt = AsyncMock(return_value="Test prompt")
        MockSessionService.return_value = mock_service_instance
        
        with patch('back.routers.gamesession.session_graph.run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            response = client.post(f"/api/gamesession/play-stream?session_id={session_id}", json={"message": user_message})
            assert response.status_code == 200
def test_play_stream_session_not_found():
    """
    Test streaming when the session ID is not found.
    This should return a standard HTTP 404 error, not a streamed error.
    """
    session_id = uuid4()
    with patch('back.routers.gamesession.GameSessionService') as MockSessionService:
        MockSessionService.side_effect = SessionNotFoundError("Session not found")
        response = client.post(f"/api/gamesession/play-stream?session_id={session_id}", json={"message": "test"})
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

def test_play_stream_valid_session():
    """
    Test streaming with a valid session and character.
    """
    session_id = uuid4()
    
    from back.graph.dto.session import GameState, DispatchResult
    from datetime import datetime
    
    mock_game_state = GameState(
        session_mode="narrative",
        narrative_history_id="default",
        combat_history_id="default"
    )
    
    expected_messages = [
        {
            "content": "Test response",
            "timestamp": datetime.now().isoformat(),
            "part_kind": "text"
        }
    ]
    
    mock_result = DispatchResult(all_messages=expected_messages, new_messages=expected_messages)

    with patch('back.routers.gamesession.GameSessionService') as MockSessionService:
        mock_service_instance = AsyncMock()
        mock_service_instance.session_id = str(session_id)
        mock_service_instance.load_game_state = AsyncMock(return_value=mock_game_state)
        mock_service_instance.update_game_state = AsyncMock()
        mock_service_instance.load_history = AsyncMock(return_value=[])
        mock_service_instance.save_history = AsyncMock()
        mock_service_instance.build_narrative_system_prompt = AsyncMock(return_value="Test prompt")
        MockSessionService.return_value = mock_service_instance
        
        # Mock the Graph execution
        with patch('back.routers.gamesession.session_graph.run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            response = client.post(f"/api/gamesession/play-stream?session_id={session_id}", json={"message": "test"})
            
            assert response.status_code == 200

def test_play_stream_internal_error():
    """
    Test streaming with a generic internal server error during setup.
    This should return a standard HTTP 500 error.
    """
    session_id = uuid4()
    with patch('back.routers.gamesession.GameSessionService') as MockSessionService:
        MockSessionService.side_effect = Exception("Generic setup error")
        response = client.post(f"/api/gamesession/play-stream?session_id={session_id}", json={"message": "test"})
        
        assert response.status_code == 500
        assert "Internal error" in response.json()["detail"]


def test_play_stream_combat_mode():
    """
    Test streaming when session is in combat mode.
    """
    session_id = uuid4()
    
    from back.graph.dto.session import GameState, DispatchResult
    from datetime import datetime
    
    mock_game_state = GameState(
        session_mode="combat",  # Combat mode
        narrative_history_id="default",
        combat_history_id="default",
        combat_state={"turn": 1, "combatants": []}
    )
    
    expected_messages = [
        {
            "content": "You strike the orc!",
            "timestamp": datetime.now().isoformat(),
            "part_kind": "text"
        }
    ]
    
    mock_result = DispatchResult(all_messages=expected_messages, new_messages=expected_messages)

    with patch('back.routers.gamesession.GameSessionService') as MockSessionService:
        mock_service_instance = AsyncMock()
        mock_service_instance.session_id = str(session_id)
        mock_service_instance.load_game_state = AsyncMock(return_value=mock_game_state)
        mock_service_instance.update_game_state = AsyncMock()
        mock_service_instance.load_history = AsyncMock(return_value=[])
        mock_service_instance.save_history = AsyncMock()
        mock_service_instance.build_combat_prompt = AsyncMock(return_value="Combat prompt")
        MockSessionService.return_value = mock_service_instance
        
        with patch('back.routers.gamesession.session_graph.run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            response = client.post(f"/api/gamesession/play-stream?session_id={session_id}", json={"message": "I attack"})
            assert response.status_code == 200
def test_play_stream_empty_message():
    """
    Test streaming with an empty message.
    """
    session_id = uuid4()
    
    from back.graph.dto.session import GameState, DispatchResult
    from datetime import datetime
    
    mock_game_state = GameState(
        session_mode="narrative",
        narrative_history_id="default",
        combat_history_id="default"
    )
    
    expected_messages = [
        {
            "content": "Please provide a valid action.",
            "timestamp": datetime.now().isoformat(),
            "part_kind": "text"
        }
    ]
    
    mock_result = DispatchResult(all_messages=expected_messages, new_messages=expected_messages)

    with patch('back.routers.gamesession.GameSessionService') as MockSessionService:
        mock_service_instance = AsyncMock()
        mock_service_instance.session_id = str(session_id)
        mock_service_instance.load_game_state = AsyncMock(return_value=mock_game_state)
        mock_service_instance.update_game_state = AsyncMock()
        mock_service_instance.load_history = AsyncMock(return_value=[])
        mock_service_instance.save_history = AsyncMock()
        mock_service_instance.build_narrative_system_prompt = AsyncMock(return_value="Test prompt")
        MockSessionService.return_value = mock_service_instance
        
        with patch('back.routers.gamesession.session_graph.run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            response = client.post(f"/api/gamesession/play-stream?session_id={session_id}", json={"message": ""})
            
            assert response.status_code == 200


def test_play_stream_no_game_state():
    """
    Test streaming when no game state exists (should create one).
    """
    session_id = uuid4()
    
    from back.graph.dto.session import GameState, DispatchResult
    from datetime import datetime
    
    expected_messages = [
        {
            "content": "Welcome to the game!",
            "timestamp": datetime.now().isoformat(),
            "part_kind": "text"
        }
    ]
    
    mock_result = DispatchResult(all_messages=expected_messages, new_messages=expected_messages)

    with patch('back.routers.gamesession.GameSessionService') as MockSessionService:
        mock_service_instance = AsyncMock()
        mock_service_instance.session_id = str(session_id)
        mock_service_instance.load_game_state = AsyncMock(return_value=None)  # No state
        mock_service_instance.update_game_state = AsyncMock()
        mock_service_instance.load_history = AsyncMock(return_value=[])
        mock_service_instance.save_history = AsyncMock()
        mock_service_instance.build_narrative_system_prompt = AsyncMock(return_value="Test prompt")
        MockSessionService.return_value = mock_service_instance
        
        with patch('back.routers.gamesession.session_graph.run', new_callable=AsyncMock) as mock_run:
            mock_run.return_value = mock_result

            response = client.post(f"/api/gamesession/play-stream?session_id={session_id}", json={"message": "start"})
            
            assert response.status_code == 200
            # Verify that update_game_state was called to create the new state
            mock_service_instance.update_game_state.assert_called()
