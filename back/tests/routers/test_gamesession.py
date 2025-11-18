from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
from back.app import app
from back.models.domain.character import Character, Stats, Skills, CombatStats
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

    with patch('back.routers.gamesession.GameSessionService.list_all_sessions', return_value=mock_sessions):
        with patch('back.routers.gamesession.CharacterPersistenceService.load_character_data', return_value=mock_character):
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
    with patch('back.routers.gamesession.GameSessionService.list_all_sessions', return_value=[]):
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

    with patch('back.routers.gamesession.GameSessionService.list_all_sessions', return_value=mock_sessions):
        with patch('back.routers.gamesession.CharacterPersistenceService.load_character_data', side_effect=FileNotFoundError):
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
    mock_session_id = uuid4()
    mock_character_id = uuid4()
    mock_scenario_name = "Test Scenario"
    mock_llm_response = "Initial narration."

    start_scenario_response = {
        "session_id": str(mock_session_id),
        "scenario_name": mock_scenario_name,
        "character_id": str(mock_character_id),
        "message": "Scenario started.",
    }

    with patch('back.routers.gamesession.GameSessionService.start_scenario', return_value=start_scenario_response):
        with patch('back.routers.gamesession.CharacterPersistenceService.load_character_data', return_value=MagicMock(status='active')):
            with patch('back.routers.gamesession.build_gm_agent_pydantic') as mock_build_agent:
                mock_agent = MagicMock()
                mock_run_result = MagicMock()
                mock_run_result.output = mock_llm_response
                mock_run_result.all_messages.return_value = []
                mock_agent.run = AsyncMock(return_value=mock_run_result)

                mock_deps = MagicMock()
                mock_deps.character_data.model_dump.return_value = {}
                mock_deps.store.save_pydantic_history.return_value = None

                mock_build_agent.return_value = (mock_agent, mock_deps)

                request_data = {
                    "scenario_name": mock_scenario_name,
                    "character_id": str(mock_character_id)
                }
                response = client.post("/api/gamesession/start", json=request_data)

                assert response.status_code == 200
                response_data = response.json()
                assert response_data["session_id"] == str(mock_session_id)
                assert response_data["scenario_name"] == mock_scenario_name
                assert response_data["character_id"] == str(mock_character_id)
                assert response_data["llm_response"] == mock_llm_response
