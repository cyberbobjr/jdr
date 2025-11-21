"""
Integration tests for scenario flows using real LLM calls.
"""

import pytest
import asyncio
from back.services.game_session_service import GameSessionService
from back.services.character_service import CharacterService
from back.services.character_data_service import CharacterDataService
from uuid import uuid4
from back.graph.graph_instance import session_graph
from back.graph.nodes.dispatcher_node import DispatcherNode
from back.graph.dto.session import SessionGraphState, PlayerMessagePayload, GameState
from back.tests.integration.helpers import load_character_from_file
from dotenv import load_dotenv

load_dotenv()

async def run_graph_message(session_service, message_content: str):
    """Helper to run the graph with a message"""
    # Load or create game_state
    game_state = await session_service.load_game_state()
    if game_state is None:
        game_state = GameState(
            session_mode="narrative",
            narrative_history_id="default",
            combat_history_id="default"
        )
        await session_service.update_game_state(game_state)

    player_message = PlayerMessagePayload(message=message_content)
    graph_state = SessionGraphState(
        game_state=game_state,
        pending_player_message=player_message
    )

    result = await session_graph.run(DispatcherNode(), state=graph_state, deps=session_service)
    return result

@pytest.mark.llm
@pytest.mark.asyncio
async def test_scenario_success_flow(temp_data_dir, test_character, test_scenario_success):
    """
    Test complete scenario success flow with LLM.
    """
    character_id, _ = test_character
    scenario_filename = test_scenario_success
    session_id = str(uuid4())
    
    # Initialize session service (creates session)
    session_service = GameSessionService(session_id, character_id, scenario_filename)
    
    # Send directive message to trigger completion
    await run_graph_message(session_service, "I complete the quest")
    
    # Verify rewards persisted
    saved_data = load_character_from_file(temp_data_dir, character_id)
    
    # Check XP (initial 0 + 100 reward)
    assert saved_data["experience_points"] == 100
    
    # Check Gold (initial 100 + 50 reward)
    assert saved_data["equipment"]["gold"] == 150

@pytest.mark.llm
@pytest.mark.asyncio
async def test_scenario_failure_flow(temp_data_dir, test_character, test_scenario_failure):
    """
    Test scenario failure flow with LLM.
    """
    character_id, _ = test_character
    scenario_filename = test_scenario_failure
    session_id = str(uuid4())
    
    # Initialize session service
    session_service = GameSessionService(session_id, character_id, scenario_filename)
    
    # Send directive message
    await run_graph_message(session_service, "I acknowledge the failure")
    
    # Verify NO rewards persisted
    saved_data = load_character_from_file(temp_data_dir, character_id)
    
    # Check XP (initial 0)
    assert saved_data["experience_points"] == 0
    
    # Check Gold (initial 100)
    assert saved_data["equipment"]["gold"] == 100

@pytest.mark.llm
@pytest.mark.asyncio
async def test_player_death_flow(temp_data_dir, test_character, test_scenario_success):
    """
    Test player death detection flow.
    """
    character_id, _ = test_character
    scenario_filename = test_scenario_success # Any scenario works
    session_id = str(uuid4())
    
    # Initialize services
    session_service = GameSessionService(session_id, character_id, scenario_filename)
    char_service = CharacterService(character_id)
    
    # Kill the player
    char_service.take_damage(1000) # Massive damage to ensure 0 HP
    
    # Send any message
    await run_graph_message(session_service, "I try to stand up")
    
    # Verify character is dead in persistence
    saved_data = load_character_from_file(temp_data_dir, character_id)
    assert saved_data["combat_stats"]["current_hit_points"] == 0
