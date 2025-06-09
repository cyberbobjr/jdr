
from pydantic_ai import RunContext
from back.services.character_service import CharacterService
from back.services.session_service import SessionService
from back.utils.logger import log_debug

svc = CharacterService()

def character_apply_xp(ctx: RunContext[SessionService], xp: int) -> dict:
    """
    Applique les XP au personnage.

    Args:
        xp (int): Le nombre d'expériences à ajouter. Ex. : 50.
    
    Returns:
        dict: Données mises à jour du personnage.
    """
    log_debug("Tool character_apply_xp appelé", tool="character_apply_xp", player_id=str(ctx.deps.character_id), xp=xp)
    return svc.apply_xp(ctx.deps.character_id, xp)

# Tool definitions removed - now handled directly by PydanticAI agent

def character_add_gold(ctx: RunContext[SessionService], gold: int) -> dict:
    """
    Ajoute de l'or au portefeuille du personnage.

    Args:
        gold (int): Montant d'or à ajouter. Ex. : 50.
    
    Returns:
        dict: Fiche personnage mise à jour.
    """
    log_debug("Tool character_add_gold appelé", tool="character_add_gold", player_id=str(ctx.deps.character_id), gold=gold)
    return svc.add_gold(ctx.deps.character_id, gold)

# Tool definition removed - now handled directly by PydanticAI agent

def character_take_damage(ctx: RunContext[SessionService], amount: int, source: str = "combat") -> dict:
    """
    Applique des dégâts au personnage (réduit ses PV).

    Args:
        amount (int): Points de dégâts à appliquer. Ex. : 10.
        source (str): Source des dégâts. Par défaut : "combat".
    
    Returns:
        dict: Fiche personnage mise à jour.
    """
    log_debug("Tool character_take_damage appelé", tool="character_take_damage", player_id=str(ctx.deps.character_id), amount=amount, source=source)
    return svc.take_damage(ctx.deps.character_id, amount, source)

# Tool definition removed - now handled directly by PydanticAI agent

# Tool definition removed - now handled directly by PydanticAI agent

# Tool definition removed - now handled directly by PydanticAI agent
