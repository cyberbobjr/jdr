import json
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from back.app import app
from back.models.domain.character import Character, CharacterStatus, Stats, Skills, CombatStats

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
    Test successful streaming of a game session response.
    """
    session_id = uuid4()
    character_id = uuid4()
    scenario_name = "TestStreamScenario"
    user_message = "I inspect the area."
    stream_chunks = ["The air is cold.", " You see a strange symbol on the wall."]
    
    final_messages = [
        {
            "kind": "request",
            "parts": [
                {
                    "content": user_message,
                    "timestamp": "2025-11-14T12:00:00Z",
                    "part_kind": "user-prompt",
                }
            ],
            "timestamp": "2025-11-14T12:00:00Z",
        },
        {
            "kind": "response",
            "parts": [
                {
                    "content": "".join(stream_chunks),
                    "timestamp": "2025-11-14T12:00:01Z",
                    "part_kind": "text",
                }
            ],
            "timestamp": "2025-11-14T12:00:01Z",
            "model_name": "test-model",
        },
    ]

    mock_stats = Stats(strength=10, constitution=10, agility=10, intelligence=10, wisdom=10, charisma=10)
    mock_skills = Skills()
    mock_combat_stats = CombatStats(max_hit_points=100, current_hit_points=100)

    mock_character = Character(
        id=character_id,
        name="Streamer",
        race="Elf",
        culture="Rivendell",
        status=CharacterStatus.ACTIVE,
        stats=mock_stats,
        skills=mock_skills,
        combat_stats=mock_combat_stats,
    )

    with patch('back.routers.gamesession.GameSessionService.get_session_info', return_value={"character_id": str(character_id), "scenario_name": scenario_name}):
        with patch('back.routers.gamesession.CharacterPersistenceService.load_character_data', return_value=mock_character):
            with patch('back.routers.gamesession.build_gm_agent_pydantic') as mock_build_agent:
                mock_agent = MagicMock()
                
                stream_result_mock = MagicMock()

                async def stream_text_generator():
                    for chunk in stream_chunks:
                        yield chunk

                def stream_text_side_effect(*args, **kwargs):
                    return stream_text_generator()

                async def empty_stream_responses(*args, **kwargs):
                    if False:
                        yield None

                stream_result_mock.stream_text.side_effect = stream_text_side_effect
                stream_result_mock.stream_responses.side_effect = lambda *args, **kwargs: empty_stream_responses()
                stream_result_mock.all_messages_json.return_value = json.dumps(final_messages)

                async_context_manager = AsyncMock()
                async_context_manager.__aenter__.return_value = stream_result_mock
                mock_agent.run_stream.return_value = async_context_manager
                
                mock_deps = MagicMock()
                mock_deps.character_data = mock_character
                mock_deps.store.load_pydantic_history.return_value = []
                
                mock_build_agent.return_value = (mock_agent, mock_deps)

                response = client.post(f"/api/gamesession/play-stream?session_id={session_id}", json={"message": user_message})

                assert response.status_code == 200
                
                streamed_content = response.text
                lines = streamed_content.strip().split('\n\n')
                
                assert len(lines) == 2
                
                data1 = json.loads(lines[0].replace('data: ', ''))
                assert data1['content'] == stream_chunks[0]
                
                data2 = json.loads(lines[1].replace('data: ', ''))
                assert data2['content'] == stream_chunks[1]

                mock_deps.store.save_pydantic_history.assert_called_once()
                saved_history = mock_deps.store.save_pydantic_history.call_args[0][0]
                assert len(saved_history) == len(final_messages)


def test_play_stream_session_not_found():
    """
    Test streaming when the session ID is not found.
    This should return a standard HTTP 404 error, not a streamed error.
    """
    session_id = uuid4()
    with patch('back.routers.gamesession.GameSessionService.get_session_info', side_effect=FileNotFoundError("Session not found")):
        response = client.post(f"/api/gamesession/play-stream?session_id={session_id}", json={"message": "test"})
        
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]

def test_play_stream_character_in_creation():
    """
    Test streaming when the character is still in creation.
    This should return a standard HTTP 400 error.
    """
    session_id = uuid4()
    character_id = uuid4()
    
    mock_stats = Stats(strength=10, constitution=10, agility=10, intelligence=10, wisdom=10, charisma=10)
    mock_skills = Skills()
    mock_combat_stats = CombatStats(max_hit_points=100, current_hit_points=100)
    
    # Use a real Character object with DRAFT status
    mock_character = Character(
        id=character_id,
        name="Drafty",
        race="Dwarf",
        culture="Erebor",
        status=CharacterStatus.DRAFT,
        stats=mock_stats,
        skills=mock_skills,
        combat_stats=mock_combat_stats,
    )

    with patch('back.routers.gamesession.GameSessionService.get_session_info', return_value={"character_id": str(character_id), "scenario_name": "test"}):
        with patch('back.routers.gamesession.CharacterPersistenceService.load_character_data', return_value=mock_character):
            response = client.post(f"/api/gamesession/play-stream?session_id={session_id}", json={"message": "test"})
            
            assert response.status_code == 400
            assert "Cannot play with a character in creation" in response.json()["detail"]

def test_play_stream_internal_error():
    """
    Test streaming with a generic internal server error during setup.
    This should return a standard HTTP 500 error.
    """
    session_id = uuid4()
    with patch('back.routers.gamesession.GameSessionService.get_session_info', side_effect=Exception("Generic setup error")):
        response = client.post(f"/api/gamesession/play-stream?session_id={session_id}", json={"message": "test"})
        
        assert response.status_code == 500
        assert "Generic setup error" in response.json()["detail"]
