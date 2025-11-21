import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from back.services.game_session_service import GameSessionService
from back.tools.skill_tools import skill_check_with_character
from back.models.domain.character import Character, Stats, Skills, CombatStats


@pytest.fixture
def mock_session_service():
    """Create a mock GameSessionService"""
    service = MagicMock(spec=GameSessionService)
    service.character_id = str(uuid4())
    return service


@pytest.fixture
def mock_run_context(mock_session_service):
    """Create a mock RunContext with the session service"""
    mock_model = MagicMock()
    usage = RunUsage(requests=1)
    return RunContext(
        deps=mock_session_service, 
        retry=0, 
        tool_name="test_tool", 
        model=mock_model, 
        usage=usage
    )


@pytest.fixture
def sample_character():
    """Create a sample Character object for testing"""
    stats = Stats(
        strength=12,
        constitution=14,
        agility=10,
        intelligence=13,
        wisdom=11,
        charisma=15
    )
    
    skills = Skills(
        artistic={"comedy": 3, "storytelling": 2},
        magic_arts={"alchemy": 2},
        athletic={"acrobatics": 4, "climbing": 2},
        combat={"weapon_handling": 5},
        concentration={"mental_concentration": 3},
        general={"perception": 6, "crafting": 2}
    )
    
    combat_stats = CombatStats(
        max_hit_points=100,
        current_hit_points=100,
        armor_class=12
    )
    
    return Character(
        name="Test Hero",
        race="human",
        culture="gondor",
        stats=stats,
        skills=skills,
        combat_stats=combat_stats
    )


@patch('back.tools.skill_tools.CharacterService')
@patch('back.tools.skill_tools.random.randint')
def test_skill_check_base_stat(mock_randint, mock_character_service, mock_run_context, sample_character):
    """Test skill check using a base stat (charisma)"""
    # Setup mocks
    mock_randint.return_value = 40  # Roll 40
    
    mock_character_instance = MagicMock()
    mock_character_instance.get_character.return_value = sample_character
    mock_character_service.return_value = mock_character_instance
    
    # Execute - charisma is 15, so skill_value = 15 * 5 = 75
    result = skill_check_with_character(mock_run_context, "charisma", "normal")
    
    # Assert
    assert result["skill_name"] == "charisma"
    assert "Base stat Charisma" in result["source_used"]
    assert result["roll"] == 40
    assert result["success"] is True
    assert "Success" in result["degree"]
    assert "Skill check for charisma" in result["message"]


@patch('back.tools.skill_tools.CharacterService')
@patch('back.tools.skill_tools.random.randint')
def test_skill_check_trained_skill(mock_randint, mock_character_service, mock_run_context, sample_character):
    """Test skill check using a trained skill (perception)"""
    # Setup mocks
    mock_randint.return_value = 50  # Roll 50
    
    mock_character_instance = MagicMock()
    mock_character_instance.get_character.return_value = sample_character
    mock_character_service.return_value = mock_character_instance
    
    # Execute - perception rank is 6, so skill_value = (10 * 5) + (6 * 10) = 110
    result = skill_check_with_character(mock_run_context, "perception", "normal")
    
    # Assert
    assert result["skill_name"] == "perception"
    assert "Skill perception (rank 6)" in result["source_used"]
    assert result["success"] is True
    assert "Skill check for perception" in result["message"]


@patch('back.tools.skill_tools.CharacterService')
@patch('back.tools.skill_tools.random.randint')
def test_skill_check_untrained_skill(mock_randint, mock_character_service, mock_run_context, sample_character):
    """Test skill check using an untrained skill (defaults to wisdom)"""
    # Setup mocks
    mock_randint.return_value = 40  # Roll 40
    
    mock_character_instance = MagicMock()
    mock_character_instance.get_character.return_value = sample_character
    mock_character_service.return_value = mock_character_instance
    
    # Execute - wisdom is 11, so skill_value = 11 * 5 = 55
    result = skill_check_with_character(mock_run_context, "unknown_skill", "normal")
    
    # Assert
    assert result["skill_name"] == "unknown_skill"
    assert "Untrained skill (using Wisdom base: 11)" in result["source_used"]
    assert result["target"] == 55
    assert "Skill check for unknown_skill" in result["message"]


@patch('back.tools.skill_tools.CharacterService')
@patch('back.tools.skill_tools.random.randint')
def test_skill_check_with_difficulty(mock_randint, mock_character_service, mock_run_context, sample_character):
    """Test skill check with difficulty modifier"""
    # Setup mocks
    mock_randint.return_value = 60  # Roll 60
    
    mock_character_instance = MagicMock()
    mock_character_instance.get_character.return_value = sample_character
    mock_character_service.return_value = mock_character_instance
    
    # Execute with unfavorable difficulty (+20)
    # strength is 12, so skill_value = 12 * 5 = 60
    # target = 60 - 20 = 40
    # roll = 60, so it's a failure
    result = skill_check_with_character(mock_run_context, "strength", "unfavorable")
    
    # Assert
    assert result["skill_name"] == "strength"
    assert result["target"] == 40
    assert result["success"] is False
    assert "Failure" in result["degree"]


@patch('back.tools.skill_tools.CharacterService')
@patch('back.tools.skill_tools.random.randint')
def test_skill_check_critical_success(mock_randint, mock_character_service, mock_run_context, sample_character):
    """Test skill check resulting in critical success"""
    # Setup mocks
    mock_randint.return_value = 1  # Roll 1 (very low)
    
    mock_character_instance = MagicMock()
    mock_character_instance.get_character.return_value = sample_character
    mock_character_service.return_value = mock_character_instance
    
    # Execute - charisma is 15, so skill_value = 75, target = 75
    # margin = 74, which is >= 50, so Critical Success
    result = skill_check_with_character(mock_run_context, "charisma", "normal")
    
    # Assert
    assert result["degree"] == "Critical Success"
    assert result["success"] is True


@patch('back.tools.skill_tools.CharacterService')
def test_skill_check_error(mock_character_service, mock_run_context):
    """Test skill check error handling"""
    # Setup mocks to raise exception
    mock_character_service.side_effect = Exception("Service error")
    
    # Execute
    result = skill_check_with_character(mock_run_context, "perception")
    
    # Assert
    assert "error" in result
    assert "Error during skill check for perception" in result["error"]
    assert "Service error" in result["error"]
