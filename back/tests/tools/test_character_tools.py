import pytest
from unittest.mock import MagicMock
from uuid import uuid4
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from back.services.game_session_service import GameSessionService
from back.tools.character_tools import character_apply_xp, character_add_gold, character_take_damage
from back.models.domain.character import Character

@pytest.fixture
def mock_session_service():
    service = MagicMock(spec=GameSessionService)
    service.character_id = str(uuid4())
    service.character_service = MagicMock()
    return service

@pytest.fixture
def mock_run_context(mock_session_service):
    mock_model = MagicMock()
    usage = RunUsage(requests=1)
    return RunContext(deps=mock_session_service, retry=0, tool_name="test_tool", model=mock_model, usage=usage)

def test_character_apply_xp(mock_run_context):
    mock_updated_character = MagicMock(spec=Character)
    mock_updated_character.xp = 150
    mock_updated_character.level = 2
    
    mock_run_context.deps.character_service.apply_xp.return_value = mock_updated_character
    
    result = character_apply_xp(mock_run_context, 50)
    
    mock_run_context.deps.character_service.apply_xp.assert_called_once_with(50)
    assert result["total_xp"] == 150
    assert result["level"] == 2
    assert "50 XP applied" in result["message"]

def test_character_add_gold(mock_run_context):
    mock_updated_character = MagicMock(spec=Character)
    mock_updated_character.gold = 200.0
    
    mock_run_context.deps.character_service.add_gold.return_value = mock_updated_character
    
    result = character_add_gold(mock_run_context, 100)
    
    mock_run_context.deps.character_service.add_gold.assert_called_once_with(100.0)
    assert result["total_gold"] == 200.0
    assert "100 gold pieces added" in result["message"]

def test_character_remove_gold(mock_run_context):
    mock_updated_character = MagicMock(spec=Character)
    mock_updated_character.gold = 50.0
    
    mock_run_context.deps.character_service.add_gold.return_value = mock_updated_character
    
    result = character_add_gold(mock_run_context, -50)
    
    mock_run_context.deps.character_service.add_gold.assert_called_once_with(-50.0)
    assert result["total_gold"] == 50.0
    assert "50 gold pieces removed" in result["message"]

def test_character_take_damage(mock_run_context):
    mock_updated_character = MagicMock(spec=Character)
    mock_updated_character.hp = 10
    
    mock_run_context.deps.character_service.take_damage.return_value = mock_updated_character
    
    result = character_take_damage(mock_run_context, 5)
    
    mock_run_context.deps.character_service.take_damage.assert_called_once_with(5, "combat")
    assert result["current_hp"] == 10
    assert result["is_alive"] is True
    assert "5 damage taken" in result["message"]
