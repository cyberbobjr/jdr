
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
    ctx.deps.character_service.apply_xp(xp)
    
    # Retourner un message simple au lieu de l'objet complexe
    return f"✅ {xp} XP appliqués au personnage. Total XP: {ctx.deps.character_service.character_data.get('xp', 0) if isinstance(ctx.deps.character_service.character_data, dict) else ctx.deps.character_service.character_data.xp}"

def character_add_gold(ctx: RunContext[SessionService], gold: int) -> str:
    """
    Ajoute de l'or au portefeuille du personnage.

    Args:
        gold (int): Montant d'or à ajouter. Ex. : 50.
    
    Returns:
        str: Message confirmant l'ajout d'or.
    """
    log_debug("Tool character_add_gold appelé", tool="character_add_gold", player_id=str(ctx.deps.character_id), gold=gold)
    ctx.deps.character_service.add_gold(gold)
    
    # Retourner un message simple au lieu de l'objet complexe
    current_gold = ctx.deps.character_service.character_data.get('gold', 0) if isinstance(ctx.deps.character_service.character_data, dict) else ctx.deps.character_service.character_data.gold
    return f"💰 {gold} pièces d'or {'ajoutées' if gold > 0 else 'retirées'}. Total: {current_gold:.2f} po"

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
    ctx.deps.character_service.take_damage(amount, source)
    
    # Retourner un message simple au lieu de l'objet complexe
    current_hp = ctx.deps.character_service.character_data.get('hp', 0) if isinstance(ctx.deps.character_service.character_data, dict) else ctx.deps.character_service.character_data.hp
    return f"💔 {amount} points de dégâts subis ({source}). PV restants: {current_hp}"


