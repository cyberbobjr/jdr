import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4
from pydantic_graph import GraphRunContext

from back.graph.nodes.dispatcher_node import DispatcherNode
from back.graph.nodes.narrative_node import NarrativeNode
from back.graph.nodes.combat_node import CombatNode
from back.graph.dto.session import SessionGraphState, GameState, PlayerMessagePayload
from back.services.game_session_service import GameSessionService, HISTORY_NARRATIVE, HISTORY_COMBAT

@pytest.fixture
def mock_session_service():
    service = MagicMock(spec=GameSessionService)
    service.session_id = str(uuid4())
    service.load_history = AsyncMock(return_value=[])
    return service

@pytest.fixture
def mock_graph_context(mock_session_service):
    game_state = GameState(session_mode="narrative")
    player_message = PlayerMessagePayload(message="Hello")
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
async def test_dispatcher_node_route_narrative(mock_graph_context):
    # Setup
    node = DispatcherNode()
    mock_graph_context.state.game_state.session_mode = "narrative"
    
    # Execute
    result = await node.run(mock_graph_context)
    
    # Assert
    assert isinstance(result, NarrativeNode)
    mock_graph_context.deps.load_history.assert_called_once_with(HISTORY_NARRATIVE)
    assert mock_graph_context.state.active_history_kind == HISTORY_NARRATIVE

@pytest.mark.asyncio
async def test_dispatcher_node_route_combat(mock_graph_context):
    # Setup
    node = DispatcherNode()
    mock_graph_context.state.game_state.session_mode = "combat"
    
    # Execute
    result = await node.run(mock_graph_context)
    
    # Assert
    assert isinstance(result, CombatNode)
    mock_graph_context.deps.load_history.assert_called_once_with(HISTORY_COMBAT)
    assert mock_graph_context.state.active_history_kind == HISTORY_COMBAT

@pytest.mark.asyncio
async def test_dispatcher_node_unknown_mode(mock_graph_context):
    # Setup
    node = DispatcherNode()
    mock_graph_context.state.game_state.session_mode = "unknown"
    
    # Execute
    result = await node.run(mock_graph_context)
    
    # Assert
    # Based on current implementation: if mode == "narrative" -> NarrativeNode, else -> CombatNode
    assert isinstance(result, CombatNode)
    # history_kind logic: if mode == "narrative" -> HISTORY_NARRATIVE, else -> HISTORY_COMBAT
    mock_graph_context.deps.load_history.assert_called_once_with(HISTORY_COMBAT)
    assert mock_graph_context.state.active_history_kind == HISTORY_COMBAT

@pytest.mark.asyncio
async def test_dispatcher_node_history_load_failure(mock_graph_context):
    # Setup
    node = DispatcherNode()
    mock_graph_context.state.game_state.session_mode = "narrative"
    
    # Mock load_history failure
    mock_graph_context.deps.load_history.side_effect = Exception("DB Error")
    
    # Execute & Assert
    with pytest.raises(Exception, match="DB Error"):
        await node.run(mock_graph_context)
    
    mock_graph_context.deps.load_history.assert_called_once_with(HISTORY_NARRATIVE)
