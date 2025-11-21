"""
Tests for scenario end functionality.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from uuid import uuid4
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from back.services.game_session_service import GameSessionService
from back.tools.scenario_tools import end_scenario_tool
from back.graph.dto.scenario import ScenarioEndPayload
from back.models.domain.character import Character, Stats, Skills, CombatStats, Equipment


@pytest.fixture
def mock_character():
    """Create a mock character"""
    stats = Stats(strength=10, constitution=10, agility=10, intelligence=10, wisdom=10, charisma=10)
    skills = Skills()
    combat_stats = CombatStats(max_hit_points=50, current_hit_points=50)
    equipment = Equipment(gold=100)
    
    character = Character(
        name="Test Hero",
        race="human",
        culture="gondor",
        stats=stats,
        skills=skills,
        combat_stats=combat_stats,
        equipment=equipment
    )
    return character


@pytest.fixture
def mock_session_service(mock_character):
    """Create a mock GameSessionService"""
    service = MagicMock(spec=GameSessionService)
    service.session_id = str(uuid4())
    service.character_id = str(uuid4())
    
    # Mock character_service
    service.character_service = MagicMock()
    service.character_service.get_character.return_value = mock_character
    service.character_service.apply_xp = MagicMock()
    service.character_service.add_gold = MagicMock()
    
    return service


@pytest.fixture
def mock_run_context(mock_session_service):
    """Create a mock RunContext"""
    mock_model = MagicMock()
    usage = RunUsage(requests=1)
    return RunContext(
        deps=mock_session_service,
        retry=0,
        tool_name="test_tool",
        model=mock_model,
        usage=usage
    )


def test_end_scenario_success_with_rewards(mock_run_context):
    """Test ending scenario with success and rewards"""
    result = end_scenario_tool(
        mock_run_context,
        outcome="success",
        summary="The hero saved the village!",
        xp_reward=100,
        gold_reward=50
    )
    
    # Verify payload structure
    assert isinstance(result, ScenarioEndPayload)
    assert result.outcome == "success"
    assert result.summary == "The hero saved the village!"
    assert result.rewards == {"xp": 100, "gold": 50}
    
    # Verify rewards were applied
    mock_run_context.deps.character_service.apply_xp.assert_called_once_with(100)
    mock_run_context.deps.character_service.add_gold.assert_called_once_with(50)


def test_end_scenario_success_no_rewards(mock_run_context):
    """Test ending scenario with success but no rewards"""
    result = end_scenario_tool(
        mock_run_context,
        outcome="success",
        summary="The quest is complete.",
        xp_reward=0,
        gold_reward=0
    )
    
    assert result.outcome == "success"
    assert result.summary == "The quest is complete."
    assert result.rewards is None
    
    # Verify no rewards were applied
    mock_run_context.deps.character_service.apply_xp.assert_not_called()
    mock_run_context.deps.character_service.add_gold.assert_not_called()


def test_end_scenario_failure(mock_run_context):
    """Test ending scenario with failure"""
    result = end_scenario_tool(
        mock_run_context,
        outcome="failure",
        summary="The village was destroyed.",
        xp_reward=0,
        gold_reward=0
    )
    
    assert result.outcome == "failure"
    assert result.summary == "The village was destroyed."
    assert result.rewards is None
    
    # Verify no rewards were applied for failure
    mock_run_context.deps.character_service.apply_xp.assert_not_called()
    mock_run_context.deps.character_service.add_gold.assert_not_called()


def test_end_scenario_failure_ignores_rewards(mock_run_context):
    """Test that failure outcome ignores any specified rewards"""
    result = end_scenario_tool(
        mock_run_context,
        outcome="failure",
        summary="The mission failed.",
        xp_reward=100,  # Should be ignored
        gold_reward=50  # Should be ignored
    )
    
    assert result.outcome == "failure"
    # Rewards should not be applied for failure
    mock_run_context.deps.character_service.apply_xp.assert_not_called()
    mock_run_context.deps.character_service.add_gold.assert_not_called()


def test_scenario_end_payload_creation():
    """Test ScenarioEndPayload model validation"""
    # Test success with rewards
    payload = ScenarioEndPayload(
        outcome="success",
        summary="Victory!",
        rewards={"xp": 100, "gold": 50}
    )
    assert payload.outcome == "success"
    assert payload.rewards["xp"] == 100
    
    # Test failure without rewards
    payload = ScenarioEndPayload(
        outcome="failure",
        summary="Defeat."
    )
    assert payload.outcome == "failure"
    assert payload.rewards is None
    
    # Test death
    payload = ScenarioEndPayload(
        outcome="death",
        summary="The hero has fallen."
    )
    assert payload.outcome == "death"
