
from pydantic_ai import RunContext
from back.services.session_service import SessionService
from back.utils.logger import log_debug

def character_apply_xp(ctx: RunContext[SessionService], xp: int) -> str:
    """
    Applique les XP au personnage.

    Args:
        xp (int): Le nombre d'expériences à ajouter. Ex. : 50.
    
    Returns:
        str: Message confirmant l'application des XP.
    """
    log_debug("Tool character_apply_xp appelé", tool="character_apply_xp", player_id=str(ctx.deps.character_id), xp=xp)
    
    # ✅ PATTERN CORRECT - Utilisation des services spécialisés via SessionService
    character = ctx.deps.apply_xp(xp)
    return f"✅ {xp} XP appliqués au personnage. Total XP: {character.xp}"

def character_add_gold(ctx: RunContext[SessionService], gold: int) -> str:
    """
    Ajoute de l'or au portefeuille du personnage.

    Args:
        gold (int): Montant d'or à ajouter. Ex. : 50.
    
    Returns:
        str: Message confirmant l'ajout d'or.
    """
    log_debug("Tool character_add_gold appelé", tool="character_add_gold", player_id=str(ctx.deps.character_id), gold=gold)
    
    # ✅ PATTERN CORRECT - Utilisation des services spécialisés via SessionService
    character = ctx.deps.add_gold(float(gold))
    return f"💰 {gold} pièces d'or {'ajoutées' if gold > 0 else 'retirées'}. Total: {character.gold:.2f} po"

def character_take_damage(ctx: RunContext[SessionService], amount: int, source: str = "combat") -> str:
    """
    Applique des dégâts au personnage (réduit ses PV).

    Args:
        amount (int): Points de dégâts à appliquer. Ex. : 10.
        source (str): Source des dégâts. Par défaut : "combat".
    
    Returns:
        str: Message confirmant l'application des dégâts.
    """
    log_debug("Tool character_take_damage appelé", tool="character_take_damage", player_id=str(ctx.deps.character_id), amount=amount, source=source)
    
    # ✅ PATTERN CORRECT - Utilisation des services spécialisés via SessionService
    character = ctx.deps.take_damage(amount, source)
    return f"💔 {amount} points de dégâts subis ({source}). PV restants: {character.hp}"
