from haystack.tools import Tool
from uuid import UUID
from back.services.character_service import CharacterService
from back.utils.logger import log_debug

svc = CharacterService()

def character_apply_xp(player_id: UUID, xp: int) -> dict:
    """
    ### character_apply_xp
    **Description :** Ajoute de l'XP à un personnage et retourne l'état mis à jour.
    **Paramètres :**
    - `player_id` (UUID) : Identifiant du personnage
    - `xp` (int) : Points d'expérience à ajouter
    **Retour :**
    - (dict) : Fiche personnage mise à jour
    """
    log_debug("Tool character_apply_xp appelé", tool="character_apply_xp", player_id=str(player_id), xp=xp)
    return svc.apply_xp(player_id, xp)

character_apply_xp_tool = Tool(
    name="character_apply_xp",
    description="Ajoute de l'XP à un personnage.",
    parameters={
        "type": "object",
        "properties": {
            "player_id": {"type": "string", "description": "Identifiant du personnage (UUID)"},
            "xp": {"type": "integer", "description": "Points d'expérience à ajouter"}
        },
        "required": ["player_id", "xp"]
    },
    function=character_apply_xp
)

def character_add_gold(player_id: UUID, gold: int) -> dict:
    """
    ### character_add_gold
    **Description :** Ajoute de l'or au portefeuille du personnage.
    **Paramètres :**
    - `player_id` (UUID) : Identifiant du personnage
    - `gold` (int) : Montant d'or à ajouter
    **Retour :**
    - (dict) : Fiche personnage mise à jour
    """
    log_debug("Tool character_add_gold appelé", tool="character_add_gold", player_id=str(player_id), gold=gold)
    return svc.add_gold(player_id, gold)

character_add_gold_tool = Tool(
    name="character_add_gold",
    description="Ajoute de l'or au portefeuille du personnage.",
    parameters={
        "type": "object",
        "properties": {
            "player_id": {"type": "string", "description": "Identifiant du personnage (UUID)"},
            "gold": {"type": "integer", "description": "Montant d'or à ajouter"}
        },
        "required": ["player_id", "gold"]
    },
    function=character_add_gold
)

def character_take_damage(player_id: UUID, amount: int, source: str = "combat") -> dict:
    """
    ### character_take_damage
    **Description :** Applique des dégâts à un personnage (réduit ses PV).
    **Paramètres :**
    - `player_id` (UUID) : Identifiant du personnage
    - `amount` (int) : Points de dégâts à appliquer
    - `source` (str) : Source des dégâts (optionnel)
    **Retour :**
    - (dict) : Fiche personnage mise à jour
    """
    log_debug("Tool character_take_damage appelé", tool="character_take_damage", player_id=str(player_id), amount=amount, source=source)
    return svc.take_damage(player_id, amount, source)

character_take_damage_tool = Tool(
    name="character_take_damage",
    description="Applique des dégâts à un personnage (réduit ses PV).",
    parameters={
        "type": "object",
        "properties": {
            "player_id": {"type": "string", "description": "Identifiant du personnage (UUID)"},
            "amount": {"type": "integer", "description": "Points de dégâts à appliquer"},
            "source": {"type": "string", "description": "Source des dégâts", "default": "combat"}
        },
        "required": ["player_id", "amount"]
    },
    function=character_take_damage
)
