from back.tools.combat_tools import perform_attack_tool
from back.models.domain.combat_manager import CombatManager
from back.utils.logger import log_debug

# Logique métier unitaire (SRP)

def perform_attack(dice: str) -> int:
    """
    Effectue un jet d'attaque en utilisant l'outil Haystack perform_attack_tool.

    Parameters:
    - dice (str): La notation des dés à lancer (ex: "1d20").

    Returns:
    - int: Le résultat du jet d'attaque.
    """
    log_debug("Jet d'attaque LLM", action="perform_attack", dice=dice)
    return perform_attack_tool(dice)
