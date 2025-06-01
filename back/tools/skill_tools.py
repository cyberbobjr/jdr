from haystack.tools import Tool
import random
from back.utils.logger import log_debug

def skill_check(skill_level: int, difficulty: int) -> bool:
    """
    ### skill_check
    **Description :** Effectue un test de compétence en comparant un jet de dé au niveau de compétence.
    **Paramètres :**
    - `skill_level` (int) : Niveau de compétence du personnage.
    - `difficulty` (int) : Difficulté du test.
    **Retour :**
    - (bool) : True si le test est réussi, False sinon.
    """
    log_debug("Tool skill_check appelé", tool="skill_check", skill_level=skill_level, difficulty=difficulty)
    roll = random.randint(1, 100)
    return roll <= skill_level - difficulty

skill_check_tool = Tool(
    name="skill_check",
    description="Effectue un test de compétence (1d100 <= skill_level - difficulty)",
    parameters={
        "skill_level": {"type": "integer", "description": "Niveau de compétence du personnage"},
        "difficulty": {"type": "integer", "description": "Difficulté du test"}
    },
    function=skill_check
)
