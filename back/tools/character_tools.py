
from pydantic_ai import RunContext
from back.services.session_service import SessionService
from back.utils.logger import log_debug

def character_apply_xp(ctx: RunContext[SessionService], xp: int) -> dict:
    """
    Applique les XP au personnage.

    Args:
        xp (int): Le nombre d'expériences à ajouter. Ex. : 50.
    
    Returns:
        dict: Données mises à jour du personnage.
    """
    log_debug("Tool character_apply_xp appelé", tool="character_apply_xp", player_id=str(ctx.deps.character_id), xp=xp)
    ctx.deps.character_service.apply_xp(xp)
    return {"character": ctx.deps.character_service.character_data.model_dump()}

def character_add_gold(ctx: RunContext[SessionService], gold: int) -> dict:
    """
    Ajoute de l'or au portefeuille du personnage.

    Args:
        gold (int): Montant d'or à ajouter. Ex. : 50.
    
    Returns:
        dict: Fiche personnage mise à jour.
    """
    log_debug("Tool character_add_gold appelé", tool="character_add_gold", player_id=str(ctx.deps.character_id), gold=gold)
    ctx.deps.character_service.add_gold(gold)
    return {"character": ctx.deps.character_service.character_data.model_dump()}

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
    ctx.deps.character_service.take_damage(amount, source)
    return {"character": ctx.deps.character_service.character_data.model_dump()}


