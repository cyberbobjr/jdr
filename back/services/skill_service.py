from back.tools.skill_tools import skill_check
from back.utils.logger import log_debug

# Logique métier unitaire (SRP)

def perform_skill_check(skill_level: int, difficulty: int) -> bool:
    """
    Effectue un test de compétence en utilisant l'outil Haystack skill_check.

    Parameters:
    - skill_level (int): Le niveau de compétence du personnage.
    - difficulty (int): La difficulté du test.

    Returns:
    - bool: True si le test est réussi, False sinon.
    """
    log_debug("Test de compétence LLM", action="perform_skill_check", skill_level=skill_level, difficulty=difficulty)
    return skill_check(skill_level=skill_level, difficulty=difficulty)
