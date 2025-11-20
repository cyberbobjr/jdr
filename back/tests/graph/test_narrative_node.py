import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4
from pydantic_graph import GraphRunContext, End

from back.graph.nodes.narrative_node import NarrativeNode
from back.graph.dto.session import SessionGraphState, GameState, PlayerMessagePayload, DispatchResult
from back.services.game_session_service import GameSessionService
from back.graph.dto.combat import CombatSeedPayload

@pytest.fixture
def mock_session_service():
    service = MagicMock(spec=GameSessionService)
    service.session_id = str(uuid4())
    service.build_narrative_system_prompt = AsyncMock(return_value="System Prompt")
    service.save_history = AsyncMock()
    service.update_game_state = AsyncMock()
    return service

@pytest.fixture
def mock_graph_context(mock_session_service):
    game_state = GameState()
    player_message = PlayerMessagePayload(message="Hello")
    state = SessionGraphState(
        game_state=game_state,
        pending_player_message=player_message,
        model_messages=[]
    )
    
    # Mock the history (state.history) if needed, but here we use model_messages
    
    return GraphRunContext(
        deps=mock_session_service,
        state=state
    )

@pytest.mark.asyncio
async def test_narrative_node_run_normal(mock_graph_context):
    # Setup
    node = NarrativeNode()
    
    # Mock the agent run result
    mock_result = MagicMock()
    mock_result.output = "Narrative response"
    mock_result.all_messages.return_value = []
    mock_result.all_messages_json.return_value = "[]"
    mock_result.new_messages_json.return_value = "[]"
    
    node.narrative_agent.run = AsyncMock(return_value=mock_result)
    
    # Execute
    result = await node.run(mock_graph_context)
    
    # Assert
    assert isinstance(result, End)
    assert isinstance(result.data, DispatchResult)
    assert mock_graph_context.state.game_state.session_mode == "narrative"
    mock_graph_context.deps.save_history.assert_called_once()

@pytest.mark.asyncio
async def test_narrative_node_run_combat_transition(mock_graph_context):
    # Setup
    node = NarrativeNode()
    
    # Mock the agent run result returning CombatSeedPayload
    seed_payload = CombatSeedPayload(
        location="Forest",
        description="Ambush",
        participants={"1": {"name": "Orc"}}
    )
    
    mock_result = MagicMock()
    mock_result.output = seed_payload
    mock_result.all_messages.return_value = []
    mock_result.all_messages_json.return_value = "[]"
    mock_result.new_messages_json.return_value = "[]"
    
    node.narrative_agent.run = AsyncMock(return_value=mock_result)
    
    # Mock CombatStateService loading
    with patch('back.services.combat_state_service.CombatStateService') as MockServiceClass:
        mock_service_instance = MockServiceClass.return_value
        
        mock_combat_state = MagicMock()
        mock_combat_state.model_dump.return_value = {"id": "combat-1", "participants": []}
        
        mock_service_instance.load_combat_state.return_value = mock_combat_state
        
        # Execute
        result = await node.run(mock_graph_context)
        
        # Assert
        assert isinstance(result, End)
        assert mock_graph_context.state.game_state.session_mode == "combat"
        assert mock_graph_context.state.game_state.combat_state == {"id": "combat-1", "participants": []}
        
        mock_service_instance.load_combat_state.assert_called_once()
        mock_graph_context.deps.update_game_state.assert_called_once()

@pytest.mark.asyncio
async def test_narrative_node_combat_load_failure(mock_graph_context):
    # Setup
    node = NarrativeNode()
    
    # Mock the agent run result returning CombatSeedPayload
    seed_payload = CombatSeedPayload(
        location="Forest",
        description="Ambush",
        participants={"1": {"name": "Orc"}}
    )
    
    mock_result = MagicMock()
    mock_result.output = seed_payload
    mock_result.all_messages.return_value = []
    mock_result.all_messages_json.return_value = "[]"
    mock_result.new_messages_json.return_value = "[]"
    
    node.narrative_agent.run = AsyncMock(return_value=mock_result)
    
    # Mock CombatStateService loading failure
    with patch('back.services.combat_state_service.CombatStateService') as MockServiceClass:
        mock_service_instance = MockServiceClass.return_value
        
        # Simulate returning None (not found)
        mock_service_instance.load_combat_state.return_value = None
        
        # Execute
        result = await node.run(mock_graph_context)
        
        # Assert
        assert isinstance(result, End)
        assert mock_graph_context.state.game_state.session_mode == "combat"
        # Combat state should remain None or whatever it was, but not updated with new state
        assert mock_graph_context.state.game_state.combat_state is None
        
        mock_service_instance.load_combat_state.assert_called_once()
        mock_graph_context.deps.update_game_state.assert_called_once()
