import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4
from pydantic_graph import GraphRunContext, End

from back.graph.nodes.combat_node import CombatNode
from back.graph.dto.session import SessionGraphState, GameState, PlayerMessagePayload, DispatchResult
from back.services.game_session_service import GameSessionService
from back.graph.dto.combat import CombatTurnEndPayload

@pytest.fixture
def mock_session_service():
    service = MagicMock(spec=GameSessionService)
    service.session_id = str(uuid4())
    service.build_combat_prompt = AsyncMock(return_value="Combat Prompt")
    service.save_history = AsyncMock()
    service.update_game_state = AsyncMock()
    return service

@pytest.fixture
def mock_graph_context(mock_session_service):
    game_state = GameState(
        session_mode="combat",
        active_combat_id="combat-1"
    )
    player_message = PlayerMessagePayload(message="Attack")
    state = SessionGraphState(
        game_state=game_state,
        pending_player_message=player_message,
        model_messages=[]
    )
    
    return GraphRunContext(
        deps=mock_session_service,
        state=state
    )

@pytest.mark.asyncio
async def test_combat_node_run_continue(mock_graph_context):
    # Setup
    node = CombatNode()
    
    # Mock the agent run result (normal turn)
    mock_result = MagicMock()
    mock_result.output = "Turn continues"
    mock_result.all_messages.return_value = []
    mock_result.all_messages_json.return_value = "[]"
    mock_result.new_messages_json.return_value = "[]"
    
    node.combat_agent.run = AsyncMock(return_value=mock_result)
    
    # Mock CombatStateService
    with patch('back.services.combat_state_service.CombatStateService') as MockServiceClass:
        mock_service_instance = MockServiceClass.return_value
        mock_service_instance.load_combat_state.return_value = {"id": "combat-1", "participants": []}
        
        # Execute
        result = await node.run(mock_graph_context)
        
        # Assert
        assert isinstance(result, End)
        assert isinstance(result.data, DispatchResult)
        assert mock_graph_context.state.game_state.session_mode == "combat"
        # combat_state is no longer in GameState
        mock_graph_context.deps.save_history.assert_called_once()
        mock_graph_context.deps.update_game_state.assert_called_once()

@pytest.mark.asyncio
async def test_combat_node_run_end(mock_graph_context):
    # Setup
    node = CombatNode()
    
    # Mock the agent run result returning CombatTurnEndPayload
    end_payload = CombatTurnEndPayload(
        combat_summary="Victory",
        winners=["Player"],
        combatants_outcomes=[],
        events=[]
    )
    
    mock_result = MagicMock()
    mock_result.output = end_payload
    mock_result.all_messages.return_value = []
    mock_result.all_messages_json.return_value = "[]"
    mock_result.new_messages_json.return_value = "[]"
    
    node.combat_agent.run = AsyncMock(return_value=mock_result)
    
    # Mock CombatStateService
    with patch('back.services.combat_state_service.CombatStateService') as MockServiceClass:
        mock_service_instance = MockServiceClass.return_value
        mock_service_instance.load_combat_state.return_value = {"id": "combat-1", "participants": []}
        
        # Execute
        result = await node.run(mock_graph_context)
        
        # Assert
        assert isinstance(result, End)
        assert mock_graph_context.state.game_state.session_mode == "narrative"
        assert mock_graph_context.state.game_state.active_combat_id is None
        assert mock_graph_context.state.game_state.last_combat_result == end_payload.model_dump()
        
        mock_graph_context.deps.update_game_state.assert_called_once()
