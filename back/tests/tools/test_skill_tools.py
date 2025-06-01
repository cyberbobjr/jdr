import pytest
from back.tools.skill_tools import skill_check_tool
from langchain.tools import tool
from unittest.mock import patch

@patch('random.randint', return_value=60)
def test_skill_check_success(mock_randint):
    input_data = {"skill_level": 80, "difficulty": 20}
    result = skill_check_tool.invoke(**input_data)
    assert result is True

def test_skill_check_failure():
    # On ne passe que les paramètres supportés par la fonction
    assert skill_check_tool.invoke(skill_level=10, difficulty=50) is False
