from back.tools.skill_tools import skill_check_tool
from unittest.mock import patch
import json

@patch('random.randint', return_value=60)
def test_skill_check_success(mock_randint):
    # Prépare un personnage avec la compétence testée
    character = {
        "competences": {"Perception": 80},
        "caracteristiques": {"Intuition": 70}
    }
    input_data = {
        "skill_name": "Perception",
        "character_json": json.dumps(character),
        "difficulty_name": "Moyenne"
    }
    result = skill_check_tool.invoke(**input_data)
    assert "Réussite" in result or "Succès" in result

def test_skill_check_failure():
    # Prépare un personnage avec une compétence faible
    character = {
        "competences": {"Perception": 10},
        "caracteristiques": {"Intuition": 10}
    }
    input_data = {
        "skill_name": "Perception",
        "character_json": json.dumps(character),
        "difficulty_name": "Très Difficile"
    }
    result = skill_check_tool.invoke(**input_data)
    assert "Échec" in result or "Echec" in result
