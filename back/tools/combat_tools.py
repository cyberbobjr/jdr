from pydantic_ai import RunContext
from back.utils.dice import roll_attack
from back.utils.logger import log_debug
from back.services.combat_service import CombatService
from back.services.session_service import SessionService
import uuid

combat_service = CombatService()

def roll_initiative_tool(ctx: RunContext[SessionService], characters: list[dict]) -> list:
    """
    Calcule l'ordre d'initiative des personnages.

    Args:
        characters (list[dict]): Liste des personnages participant au combat.
    
    Returns:
        list: Liste triée selon l'initiative.
    """
    log_debug("Tool roll_initiative_tool appelé", tool="roll_initiative_tool", characters=characters)
    # Ensure each character has an 'id' for CombatState
    for c in characters:
        if 'id' not in c:
            c['id'] = str(uuid.uuid4())
    # Utilisation de CombatService pour l'initiative
    state = combat_service.start_combat(characters)
    state = combat_service.roll_initiative(state)
    # Retourne la liste triée des personnages selon l'ordre d'initiative
    return [p for cid in state.initiative_order for p in state.participants if p['id'] == cid]

# Tool definition removed - now handled directly by PydanticAI agent

def perform_attack_tool(ctx: RunContext[SessionService], dice: str) -> int:
    """
    Effectue un jet d'attaque.

    Args:
        dice (str): Notation des dés à lancer. Ex. : "1d20".
    
    Returns:
        int: Résultat du jet d'attaque.
    """
    log_debug("Tool perform_attack_tool appelé", tool="perform_attack_tool", dice=dice)
    return roll_attack(dice)

# Tool definition removed - now handled directly by PydanticAI agent

def resolve_attack_tool(ctx: RunContext[SessionService], attack_roll: int, defense_roll: int) -> bool:
    """
    Résout une attaque en comparant les jets d'attaque et de défense.

    Args:
        attack_roll (int): Résultat du jet d'attaque.
        defense_roll (int): Résultat du jet de défense.
    
    Returns:
        bool: True si l'attaque réussit, False sinon.
    """
    log_debug("Tool resolve_attack_tool appelé", tool="resolve_attack_tool", attack_roll=attack_roll, defense_roll=defense_roll)
    return attack_roll > defense_roll

# Tool definition removed - now handled directly by PydanticAI agent

def calculate_damage_tool(ctx: RunContext[SessionService], base_damage: int, bonus: int = 0) -> int:
    """
    Calcule les dégâts infligés en tenant compte des modificateurs.

    Args:
        base_damage (int): Dégâts de base de l'attaque.
        bonus (int): Bonus/malus de dégâts. Par défaut : 0.
    
    Returns:
        int: Dégâts finaux infligés.
    """
    log_debug("Tool calculate_damage_tool appelé", tool="calculate_damage_tool", base_damage=base_damage, bonus=bonus)
    # Utilisation de CombatService pour le calcul des dégâts
    return max(0, base_damage + bonus)

# Tool definition removed - now handled directly by PydanticAI agent

def end_combat_tool(ctx: RunContext[SessionService], combat_id: str, reason: str) -> dict:
    """
    Termine explicitement un combat en précisant la raison.

    Args:
        combat_id (str): Identifiant du combat.
        reason (str): Raison de la fin du combat (fuite, reddition, victoire, etc.).
    
    Returns:
        dict: Dictionnaire contenant le statut final du combat.
    """
    # Ici, il faudrait charger le CombatState depuis la persistance (non implémenté)
    # combat_state = charger_combat_state(combat_id)
    # combat_state = combat_service.end_combat(combat_state, reason)
    # sauvegarder_combat_state(combat_state)
    # return combat_service.get_combat_summary(combat_state)
    return {"combat_id": combat_id, "status": "termine", "end_reason": reason}

# Tool definition removed - now handled directly by PydanticAI agent
