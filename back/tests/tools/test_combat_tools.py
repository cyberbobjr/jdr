import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from back.services.game_session_service import GameSessionService
from back.tools.combat_tools import (
    execute_attack_tool,
    apply_direct_damage_tool,
    end_combat_tool,
    end_turn_tool,
    check_combat_end_tool,
    get_combat_status_tool,
    start_combat_tool
)
from back.models.domain.combat_state import CombatState, Combatant, CombatantType

@pytest.fixture
def mock_session_service():
    service = MagicMock(spec=GameSessionService)
    service.session_id = str(uuid4())
    return service

@pytest.fixture
def mock_run_context(mock_session_service):
    mock_model = MagicMock()
    usage = RunUsage(requests=1)
    return RunContext(deps=mock_session_service, retry=0, tool_name="test_tool", model=mock_model, usage=usage)

@patch('back.tools.combat_tools.combat_state_service')
@patch('back.tools.combat_tools.combat_service')
def test_execute_attack_tool(mock_combat_service, mock_combat_state_service, mock_run_context):
    combat_id = "combat-123"
    attacker_id = "attacker-1"
    target_id = "target-1"
    
    mock_state = MagicMock(spec=CombatState)
    mock_state.id = combat_id
    
    mock_combat_state_service.load_combat_state.return_value = mock_state
    
    # Mock successful attack result
    mock_combat_service.execute_attack.return_value = (mock_state, "Hit! 5 damage.")
    mock_combat_service.check_combat_end.return_value = False
    mock_combat_service.get_combat_summary.return_value = {"status": "ongoing"}
    
    result = execute_attack_tool(mock_run_context, attacker_id, target_id)
    
    mock_combat_service.execute_attack.assert_called_once_with(mock_state, attacker_id, target_id)
    mock_combat_state_service.save_combat_state.assert_called_once()
    assert result["message"] == "Hit! 5 damage."
    assert result["auto_ended"] is None

@patch('back.tools.combat_tools.combat_state_service')
@patch('back.tools.combat_tools.combat_service')
def test_execute_attack_tool_ends_combat(mock_combat_service, mock_combat_state_service, mock_run_context):
    combat_id = "combat-123"
    attacker_id = "attacker-1"
    target_id = "target-1"
    
    mock_state = MagicMock(spec=CombatState)
    mock_state.id = combat_id
    # Mock participants for end check
    p1 = MagicMock(spec=Combatant)
    p1.type = CombatantType.PLAYER
    p1.is_alive.return_value = True
    p2 = MagicMock(spec=Combatant)
    p2.type = CombatantType.NPC
    p2.is_alive.return_value = False # Enemy dead
    mock_state.participants = [p1, p2]
    
    mock_combat_state_service.load_combat_state.return_value = mock_state
    mock_combat_service.execute_attack.return_value = (mock_state, "Hit! Enemy dead.")
    mock_combat_service.check_combat_end.return_value = True
    mock_combat_service.end_combat.return_value = mock_state
    
    result = execute_attack_tool(mock_run_context, attacker_id, target_id)
    
    mock_combat_service.end_combat.assert_called_once_with(mock_state, "victory")
    mock_combat_state_service.delete_combat_state.assert_called_once()
    assert result["auto_ended"]["ended"] is True
    assert result["auto_ended"]["reason"] == "victory"

@patch('back.tools.combat_tools.combat_state_service')
@patch('back.tools.combat_tools.combat_service')
def test_apply_direct_damage_tool(mock_combat_service, mock_combat_state_service, mock_run_context):
    combat_id = "combat-123"
    target_id = "target-1"
    amount = 10
    
    mock_state = MagicMock(spec=CombatState)
    mock_state.id = combat_id
    
    mock_combat_state_service.load_combat_state.return_value = mock_state
    mock_combat_service.apply_direct_damage.return_value = mock_state
    mock_combat_service.check_combat_end.return_value = False
    mock_combat_service.get_combat_summary.return_value = {}
    
    result = apply_direct_damage_tool(mock_run_context, target_id, amount, "Fireball")
    
    mock_combat_service.apply_direct_damage.assert_called_once_with(mock_state, target_id, amount, is_attack=False)
    mock_combat_state_service.save_combat_state.assert_called_once()
    assert "Applied 10 damage" in result["message"]

@patch('back.tools.combat_tools.combat_state_service')
@patch('back.tools.combat_tools.combat_service')
def test_end_combat_tool(mock_combat_service, mock_combat_state_service, mock_run_context):
    combat_id = "combat-123"
    mock_state = MagicMock(spec=CombatState)
    mock_state.id = combat_id
    
    mock_combat_state_service.load_combat_state.return_value = mock_state
    mock_combat_service.end_combat.return_value = mock_state
    mock_combat_service.get_combat_summary.return_value = {"status": "ended"}
    
    result = end_combat_tool(mock_run_context, combat_id, "victory")
    
    mock_combat_service.end_combat.assert_called_once_with(mock_state, "victory")
    mock_combat_state_service.delete_combat_state.assert_called_once()
    assert result["status"] == "ended"

@patch('back.tools.combat_tools.combat_state_service')
@patch('back.tools.combat_tools.combat_service')
def test_end_turn_tool(mock_combat_service, mock_combat_state_service, mock_run_context):
    combat_id = "combat-123"
    mock_state = MagicMock(spec=CombatState)
    mock_state.id = combat_id
    
    mock_combat_state_service.load_combat_state.return_value = mock_state
    mock_combat_service.end_turn.return_value = mock_state
    mock_combat_service.get_combat_summary.return_value = {}
    
    current_p = MagicMock()
    current_p.name = "Player"
    mock_state.get_current_combatant.return_value = current_p
    
    result = end_turn_tool(mock_run_context, combat_id)
    
    mock_combat_service.end_turn.assert_called_once()
    mock_combat_state_service.save_combat_state.assert_called_once()
    assert "Turn ended" in result["message"]

@patch('back.tools.combat_tools.combat_state_service')
@patch('back.tools.combat_tools.combat_service')
def test_check_combat_end_tool_ongoing(mock_combat_service, mock_combat_state_service, mock_run_context):
    combat_id = "combat-123"
    mock_state = MagicMock(spec=CombatState)
    mock_state.id = combat_id
    
    mock_combat_state_service.load_combat_state.return_value = mock_state
    mock_combat_service.check_combat_end.return_value = False
    
    result = check_combat_end_tool(mock_run_context, combat_id)
    
    assert result["combat_ended"] is False
    assert result["status"] == "ongoing"

@patch('back.tools.combat_tools.combat_state_service')
@patch('back.tools.combat_tools.combat_service')
def test_get_combat_status_tool(mock_combat_service, mock_combat_state_service, mock_run_context):
    combat_id = "combat-123"
    mock_state = MagicMock(spec=CombatState)
    mock_state.id = combat_id
    
    mock_combat_state_service.load_combat_state.return_value = mock_state
    mock_combat_service.get_combat_summary.return_value = {"alive_participants": []}
    
    result = get_combat_status_tool(mock_run_context, combat_id)
    
    mock_combat_service.get_combat_summary.assert_called_once()
    assert "alive_participants" in result

@patch('back.tools.combat_tools.combat_state_service')
@patch('back.tools.combat_tools.combat_service')
def test_start_combat_tool(mock_combat_service, mock_combat_state_service, mock_run_context):
    mock_combat_state_service.has_active_combat.return_value = False
    
    mock_state = MagicMock(spec=CombatState)
    mock_state.id = uuid4()
    
    mock_combat_service.start_combat.return_value = mock_state
    
    participants = [{"name": "Player", "role": "ally"}]
    location = "Forest"
    description = "A dark forest"
    
    result = start_combat_tool(mock_run_context, location, description, participants)
    
    mock_combat_service.start_combat.assert_called_once()
    mock_combat_state_service.save_combat_state.assert_called_once()
    
    assert "combat_id" in result
    assert "message" in result
    assert location in result["message"]
