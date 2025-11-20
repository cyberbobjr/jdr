import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from back.services.game_session_service import GameSessionService
from back.tools.combat_tools import (
    roll_initiative_tool,
    perform_attack_tool,
    resolve_attack_tool,
    calculate_damage_tool,
    end_combat_tool,
    end_turn_tool,
    check_combat_end_tool,
    apply_damage_tool,
    get_combat_status_tool,
    start_combat_tool
)
from back.models.domain.combat_state import CombatState, Combatant

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

@patch('back.tools.combat_tools.combat_service')
def test_roll_initiative_tool(mock_combat_service, mock_run_context):
    # Setup
    characters = [{"name": "Player", "id": "123"}, {"name": "Enemy", "id": "456"}]
    
    mock_state = MagicMock(spec=CombatState)
    mock_state.initiative_order = ["123", "456"]
    
    p1 = MagicMock(spec=Combatant)
    p1.id = "123"
    p1.name = "Player"
    p1.initiative_roll = 15
    
    p2 = MagicMock(spec=Combatant)
    p2.id = "456"
    p2.name = "Enemy"
    p2.initiative_roll = 10
    
    mock_state.participants = [p1, p2]
    mock_state.get_combatant.side_effect = lambda uid: p1 if uid == "123" else p2
    mock_state.turn_order = ["123", "456"]
    
    mock_combat_service.start_combat.return_value = mock_state
    mock_combat_service.roll_initiative.return_value = mock_state
    
    # Execute
    result = roll_initiative_tool(mock_run_context, characters)
    
    # Assert
    mock_combat_service.start_combat.assert_called_once()
    mock_combat_service.roll_initiative.assert_called_once()
    assert len(result) == 2
    assert result[0]["name"] == "Player"
    assert result[1]["name"] == "Enemy"

@patch('back.tools.combat_tools.roll_attack')
def test_perform_attack_tool(mock_roll_attack, mock_run_context):
    mock_roll_attack.return_value = 15
    result = perform_attack_tool(mock_run_context, "1d20")
    mock_roll_attack.assert_called_once_with("1d20")
    assert result == 15

def test_resolve_attack_tool(mock_run_context):
    assert resolve_attack_tool(mock_run_context, 15, 10) is True
    assert resolve_attack_tool(mock_run_context, 10, 15) is False

def test_calculate_damage_tool(mock_run_context):
    assert calculate_damage_tool(mock_run_context, 5, 2) == 7
    assert calculate_damage_tool(mock_run_context, 5, -10) == 0

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
    mock_state.is_active = True
    
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
    mock_state.is_active = True
    
    mock_combat_state_service.load_combat_state.return_value = mock_state
    mock_combat_service.check_combat_end.return_value = False
    
    result = check_combat_end_tool(mock_run_context, combat_id)
    
    assert result["combat_ended"] is False
    assert result["status"] == "ongoing"

@patch('back.tools.combat_tools.combat_state_service')
@patch('back.tools.combat_tools.combat_service')
def test_apply_damage_tool(mock_combat_service, mock_combat_state_service, mock_run_context):
    combat_id = "combat-123"
    target_id = str(uuid4())
    mock_state = MagicMock(spec=CombatState)
    mock_state.id = combat_id
    mock_state.is_active = True
    
    mock_combat_state_service.load_combat_state.return_value = mock_state
    mock_combat_service.apply_damage.return_value = mock_state
    mock_combat_service.check_combat_end.return_value = False
    mock_combat_service.get_combat_summary.return_value = {}
    
    target = MagicMock()
    target.id = target_id
    target.name = "Target"
    target.current_hit_points = 5
    mock_state.get_combatant.return_value = target
    
    result = apply_damage_tool(mock_run_context, combat_id, target_id, 5)
    
    mock_combat_service.apply_damage.assert_called_once()
    assert result["damage_applied"] == 5
    assert result["target"]["name"] == "Target"

@patch('back.tools.combat_tools.combat_state_service')
@patch('back.tools.combat_tools.combat_service')
def test_get_combat_status_tool(mock_combat_service, mock_combat_state_service, mock_run_context):
    combat_id = "combat-123"
    mock_state = MagicMock(spec=CombatState)
    mock_state.id = combat_id
    
    mock_combat_state_service.load_combat_state.return_value = mock_state
    mock_combat_service.get_combat_summary.return_value = {}
    
    mock_state.get_current_combatant.return_value = None
    mock_state.participants = []
    
    result = get_combat_status_tool(mock_run_context, combat_id)
    
    mock_combat_service.get_combat_summary.assert_called_once()
    assert "alive_participants" in result

@patch('back.tools.combat_tools.combat_state_service')
@patch('back.tools.combat_tools.combat_service')
def test_start_combat_tool(mock_combat_service, mock_combat_state_service, mock_run_context):
    mock_combat_state_service.has_active_combat.return_value = False
    
    mock_state = MagicMock(spec=CombatState)
    mock_state.current_turn = 0
    mock_state.initiative_order = ["123"]
    
    p1 = MagicMock()
    p1.id = "123"
    p1.name = "Player"
    p1.current_hit_points = 10
    p1.max_hit_points = 10
    p1.camp = "player"
    p1.type = "player"
    
    mock_state.participants = [p1]
    mock_state.get_current_combatant.return_value = p1
    
    mock_combat_service.start_combat.return_value = mock_state
    mock_combat_service.roll_initiative.return_value = mock_state
    
    participants = [{"name": "Player", "camp": "player"}]
    location = "Forest"
    description = "A dark forest"
    
    result = start_combat_tool(mock_run_context, location, description, participants)
    
    mock_combat_service.start_combat.assert_called_once()
    mock_combat_state_service.save_combat_state.assert_called_once()
    
    assert result["location"] == location
    assert result["description"] == description
    assert "participants" in result
    assert result["participants"]["123"]["name"] == "Player"
