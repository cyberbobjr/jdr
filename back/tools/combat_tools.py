from haystack.tools import Tool
from back.utils.dice import roll_attack
from back.utils.logger import log_debug
from back.services.combat_service import CombatService
import uuid

combat_service = CombatService()

def roll_initiative_tool(characters: list[dict]) -> list:
    """
    ### roll_initiative_tool
    **Description :** Calcule l'ordre d'initiative des personnages.
    **Paramètres :**
    - `characters` (list[dict]) : Liste des personnages.
    **Retour :**
    - (list) : Liste triée selon l'initiative.
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

roll_initiative = Tool(
    name="roll_initiative",
    description="Calcule l'ordre d'initiative des personnages.",
    parameters={
        "type": "object",
        "properties": {
            "characters": {"type": "array", "description": "Liste des personnages", "items": {"type": "object"}}
        },
        "required": ["characters"]
    },
    function=roll_initiative_tool
)

def perform_attack_tool(dice: str) -> int:
    """
    ### perform_attack_tool
    **Description :** Effectue un jet d'attaque.
    **Paramètres :**
    - `dice` (str) : Notation des dés à lancer (ex: "1d20").
    **Retour :**
    - (int) : Résultat du jet d'attaque.
    """
    log_debug("Tool perform_attack_tool appelé", tool="perform_attack_tool", dice=dice)
    return roll_attack(dice)

perform_attack = Tool(
    name="perform_attack",
    description="Effectue un jet d'attaque.",
    parameters={
        "type": "object",
        "properties": {
            "dice": {"type": "string", "description": "Notation des dés à lancer (ex: 1d20)"}
        },
        "required": ["dice"]
    },
    function=perform_attack_tool
)

def resolve_attack_tool(attack_roll: int, defense_roll: int) -> bool:
    """
    ### resolve_attack_tool
    **Description :** Résout une attaque en comparant les jets d'attaque et de défense.
    **Paramètres :**
    - `attack_roll` (int) : Jet d'attaque.
    - `defense_roll` (int) : Jet de défense.
    **Retour :**
    - (bool) : True si l'attaque réussit, False sinon.
    """
    log_debug("Tool resolve_attack_tool appelé", tool="resolve_attack_tool", attack_roll=attack_roll, defense_roll=defense_roll)
    return attack_roll > defense_roll

resolve_attack = Tool(
    name="resolve_attack",
    description="Résout une attaque (attaque > défense).",
    parameters={
        "type": "object",
        "properties": {
            "attack_roll": {"type": "integer", "description": "Jet d'attaque"},
            "defense_roll": {"type": "integer", "description": "Jet de défense"}
        },
        "required": ["attack_roll", "defense_roll"]
    },
    function=resolve_attack_tool
)

def calculate_damage_tool(base_damage: int, bonus: int = 0) -> int:
    """
    ### calculate_damage_tool
    **Description :** Calcule les dégâts infligés en tenant compte des modificateurs.
    **Paramètres :**
    - `base_damage` (int) : Dégâts de base de l'attaque.
    - `bonus` (int) : Bonus/malus de dégâts (optionnel).
    **Retour :**
    - (int) : Dégâts finaux infligés.
    """
    log_debug("Tool calculate_damage_tool appelé", tool="calculate_damage_tool", base_damage=base_damage, bonus=bonus)
    # Utilisation de CombatService pour le calcul des dégâts
    return max(0, base_damage + bonus)

calculate_damage = Tool(
    name="calculate_damage",
    description="Calcule les dégâts infligés en tenant compte des modificateurs.",
    parameters={
        "type": "object",
        "properties": {
            "base_damage": {"type": "integer", "description": "Dégâts de base de l'attaque"},
            "bonus": {"type": "integer", "description": "Bonus/malus de dégâts", "default": 0}
        },
        "required": ["base_damage"]
    },
    function=calculate_damage_tool
)

def end_combat_tool(combat_id: str, reason: str) -> dict:
    """
    ### end_combat_tool
    **Description :** Termine explicitement un combat en précisant la raison (fuite, reddition, etc.).
    **Paramètres :**
    - `combat_id` (str) : Identifiant du combat.
    - `reason` (str) : Raison de la fin du combat.
    **Retour :** Dictionnaire contenant le statut final du combat.
    """
    # Ici, il faudrait charger le CombatState depuis la persistance (non implémenté)
    # combat_state = charger_combat_state(combat_id)
    # combat_state = combat_service.end_combat(combat_state, reason)
    # sauvegarder_combat_state(combat_state)
    # return combat_service.get_combat_summary(combat_state)
    return {"combat_id": combat_id, "status": "termine", "end_reason": reason}

end_combat = Tool(
    name="end_combat",
    description="Termine explicitement un combat (fuite, reddition, etc.)",
    parameters={
        "type": "object",
        "properties": {
            "combat_id": {"type": "string", "description": "Identifiant du combat"},
            "reason": {"type": "string", "description": "Raison de la fin du combat (fuite, reddition, etc.)"}
        },
        "required": ["combat_id", "reason"]
    },
    function=end_combat_tool
)
