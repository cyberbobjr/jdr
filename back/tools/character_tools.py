
from pydantic_ai import RunContext
from back.services.game_session_service import GameSessionService
from back.utils.logger import log_debug

def character_apply_xp(ctx: RunContext[GameSessionService], xp: int) -> dict:
    """
    Apply experience points (XP) to the character.

    Use this tool when the character completes a quest, defeats enemies, or achieves a milestone.
    The tool automatically handles leveling up if the XP threshold is reached.

    Args:
        xp (int): The amount of XP to add. Must be a positive integer.

    Returns:
        dict: A summary of the action, including total XP and current level.
    """
    log_debug("Tool character_apply_xp called", tool="character_apply_xp", player_id=str(ctx.deps.character_id), xp=xp)
    
    # ✅ CORRECT PATTERN - Use specialized services via SessionService
    character = ctx.deps.character_service.apply_xp(xp)
    
    return {
        "message": f"✅ {xp} XP applied to character.",
        "total_xp": character.xp,
        "level": character.level if hasattr(character, 'level') else 1 # Assuming level exists or is calculated
    }

def character_add_gold(ctx: RunContext[GameSessionService], gold: int) -> dict:
    """
    Add or remove gold from the character's wallet.

    Use this tool when the character finds money, receives a reward, or pays for something 
    (if not using a specific transaction tool like inventory_add_item).
    Use negative values to remove gold.

    Args:
        gold (int): Amount of gold to add (positive) or remove (negative).

    Returns:
        dict: A summary of the transaction and the new balance.
    """
    log_debug("Tool character_add_gold called", tool="character_add_gold", player_id=str(ctx.deps.character_id), gold=gold)
    
    # ✅ CORRECT PATTERN - Use specialized services via SessionService
    character = ctx.deps.character_service.add_gold(float(gold))
    
    action = "added" if gold > 0 else "removed"
    return {
        "message": f"💰 {abs(gold)} gold pieces {action}.",
        "total_gold": character.gold
    }

def character_take_damage(ctx: RunContext[GameSessionService], amount: int, source: str = "combat") -> dict:
    """
    Apply damage to the character (reduce HP).

    Use this tool when the character gets hurt outside of the combat system (e.g., traps, falls, environmental damage).
    For combat damage, prefer using the combat tools if a combat session is active.

    Args:
        amount (int): Amount of damage to apply. Must be positive.
        source (str): The source of the damage (e.g., "trap", "fall"). Default: "combat".

    Returns:
        dict: A summary of the damage taken and remaining HP.
    """
    log_debug("Tool character_take_damage called", tool="character_take_damage", player_id=str(ctx.deps.character_id), amount=amount, source=source)
    
    # ✅ CORRECT PATTERN - Use specialized services via SessionService
    character = ctx.deps.character_service.take_damage(amount, source)
    
    return {
        "message": f"💔 {amount} damage taken from {source}.",
        "current_hp": character.hp,
        "is_alive": character.hp > 0
    }
