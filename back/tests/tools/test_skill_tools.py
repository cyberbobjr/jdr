import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4
from pydantic_ai import RunContext
from pydantic_ai.usage import RunUsage
from back.services.game_session_service import GameSessionService
from back.tools.skill_tools import skill_check_with_character

@pytest.fixture
def mock_session_service():
    service = MagicMock(spec=GameSessionService)
    service.character_id = str(uuid4())
    return service

@pytest.fixture
def mock_run_context(mock_session_service):
    mock_model = MagicMock()
    usage = RunUsage(requests=1)
    return RunContext(deps=mock_session_service, retry=0, tool_name="test_tool", model=mock_model, usage=usage)

@patch('back.tools.skill_tools.CharacterService')
@patch('back.tools.skill_tools.UnifiedSkillsManager')
@patch('back.tools.skill_tools.StatsManager')
@patch('back.tools.skill_tools.random.randint')
def test_skill_check_direct_skill(mock_randint, mock_stats_manager, mock_skills_manager, mock_character_service, mock_run_context):
    # Setup mocks
    mock_randint.return_value = 40 # Roll 40
    
    mock_character_instance = MagicMock()
    mock_character_instance.get_character.return_value = {
        "competences": {"Perception": 60},
        "caracteristiques": {},
        "culture": {}
    }
    mock_character_service.return_value = mock_character_instance
    
    # Execute
    result = skill_check_with_character(mock_run_context, "Perception", "normal")
    
    # Assert
    assert "Test de Perception" in result
    assert "Compétence Perception = 60" in result
    assert "Jet 1d100 = 40" in result
    assert "Réussite" in result

@patch('back.tools.skill_tools.CharacterService')
@patch('back.tools.skill_tools.UnifiedSkillsManager')
@patch('back.tools.skill_tools.StatsManager')
@patch('back.tools.skill_tools.random.randint')
def test_skill_check_culture_bonus(mock_randint, mock_stats_manager, mock_skills_manager, mock_character_service, mock_run_context):
    # Setup mocks
    mock_randint.return_value = 40
    
    mock_character_instance = MagicMock()
    mock_character_instance.get_character.return_value = {
        "competences": {},
        "caracteristiques": {"Raisonnement": 50},
        "culture": {"skill_bonuses": {"Histoire": 10}}
    }
    mock_character_service.return_value = mock_character_instance
    
    mock_skills_manager_instance = mock_skills_manager.return_value
    mock_skills_manager_instance.get_skill_by_name.return_value = {"primary_characteristic": "Raisonnement"}
    
    # Execute
    result = skill_check_with_character(mock_run_context, "Histoire", "normal")
    
    # Assert
    assert "Test de Histoire" in result
    assert "Raisonnement (50) + Bonus Culturel Histoire (10)" in result
    assert "= 60" in result
    assert "Réussite" in result

@patch('back.tools.skill_tools.CharacterService')
@patch('back.tools.skill_tools.UnifiedSkillsManager')
@patch('back.tools.skill_tools.StatsManager')
@patch('back.tools.skill_tools.random.randint')
def test_skill_check_characteristic(mock_randint, mock_stats_manager, mock_skills_manager, mock_character_service, mock_run_context):
    # Setup mocks
    mock_randint.return_value = 40
    
    mock_character_instance = MagicMock()
    mock_character_instance.get_character.return_value = {
        "competences": {},
        "caracteristiques": {"Force": 70},
        "culture": {}
    }
    mock_character_service.return_value = mock_character_instance
    
    # Execute
    result = skill_check_with_character(mock_run_context, "Force", "normal")
    
    # Assert
    assert "Test de Force" in result
    assert "Caractéristique Force = 70" in result
    assert "Réussite" in result

@patch('back.tools.skill_tools.CharacterService')
@patch('back.tools.skill_tools.UnifiedSkillsManager')
@patch('back.tools.skill_tools.StatsManager')
@patch('back.tools.skill_tools.random.randint')
def test_skill_check_default_fallback(mock_randint, mock_stats_manager, mock_skills_manager, mock_character_service, mock_run_context):
    # Setup mocks
    mock_randint.return_value = 40
    
    mock_character_instance = MagicMock()
    mock_character_instance.get_character.return_value = {
        "competences": {},
        "caracteristiques": {},
        "culture": {}
    }
    mock_character_service.return_value = mock_character_instance
    
    mock_skills_manager_instance = mock_skills_manager.return_value
    mock_skills_manager_instance.get_skill_by_name.return_value = None
    
    # Execute
    result = skill_check_with_character(mock_run_context, "UnknownSkill", "normal")
    
    # Assert
    assert "Test de UnknownSkill" in result
    assert "Valeur par défaut" in result
    assert "= 50" in result

@patch('back.tools.skill_tools.CharacterService')
def test_skill_check_error(mock_character_service, mock_run_context):
    # Setup mocks to raise exception
    mock_character_service.side_effect = Exception("Service error")
    
    # Execute
    result = skill_check_with_character(mock_run_context, "Perception")
    
    # Assert
    assert "Erreur lors du test de Perception" in result
    assert "Service error" in result
