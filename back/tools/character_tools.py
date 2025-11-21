from pydantic_ai import RunContext
from back.services.game_session_service import GameSessionService
from back.utils.logger import log_debug, log_warning

def character_add_currency(
    ctx: RunContext[GameSessionService], 
    gold: int = 0, 
    silver: int = 0, 
    copper: int = 0
) -> dict:
    """
    Add currency (gold, silver, copper) to the character.
    
    WHEN TO USE:
    - When the character finds money (loot, chest, etc.)
    - When the character receives a monetary reward
    
    Args:
        gold (int): Amount of gold to add. Default: 0.
        silver (int): Amount of silver to add. Default: 0.
        copper (int): Amount of copper to add. Default: 0.
    
    Returns:
        dict: Updated currency totals.
    """
    try:
        log_debug(
            "Tool character_add_currency called",
            tool="character_add_currency",
            player_id=str(ctx.deps.character_id),
            gold=gold,
            silver=silver,
            copper=copper
        )
        
        if not ctx.deps.character_service:
            return {"error": "Character service not available"}
            
        # Add currency via service
        updated_character = ctx.deps.character_service.add_currency(gold, silver, copper)
        
        return {
            "message": f"Added {gold}G {silver}S {copper}C",
            "currency": {
                "gold": updated_character.equipment.gold,
                "silver": updated_character.equipment.silver,
                "copper": updated_character.equipment.copper
            }
        }
        
    except Exception as e:
        log_warning(
            "Error in character_add_currency",
            error=str(e),
            character_id=str(ctx.deps.character_id)
        )
        return {"error": f"Failed to add currency: {str(e)}"}

def character_take_damage(ctx: RunContext[GameSessionService], damage: int, source: str = "unknown") -> dict:
    """
    Apply damage to the character.
    
    WHEN TO USE:
    - When the character takes damage from traps, environment, or narrative events outside of combat.
    
    Args:
        damage (int): Amount of damage to take.
        source (str): Source of the damage. Default: "unknown".
    
    Returns:
        dict: Updated character status (HP).
    """
    try:
        log_debug(
            "Tool character_take_damage called",
            tool="character_take_damage",
            player_id=str(ctx.deps.character_id),
            damage=damage,
            source=source
        )
        
        if not ctx.deps.character_service:
            return {"error": "Character service not available"}
            
        # Apply damage via service
        updated_character = ctx.deps.character_service.take_damage(damage, source)
        
        return {
            "message": f"Took {damage} damage from {source}",
            "current_hp": updated_character.combat_stats.current_hit_points,
            "max_hp": updated_character.combat_stats.max_hit_points,
            "is_alive": updated_character.combat_stats.is_alive()
        }
        
    except Exception as e:
        log_warning("Error in character_take_damage", error=str(e))
        return {"error": f"Failed to take damage: {str(e)}"}

def character_heal(ctx: RunContext[GameSessionService], amount: int, source: str = "magic") -> dict:
    """
    Heal the character.
    
    WHEN TO USE:
    - When the character is healed by potions, spells, or rest.
    
    Args:
        amount (int): Amount of HP to restore.
        source (str): Source of healing. Default: "magic".
    
    Returns:
        dict: Updated character status (HP).
    """
    try:
        log_debug(
            "Tool character_heal called",
            tool="character_heal",
            player_id=str(ctx.deps.character_id),
            amount=amount,
            source=source
        )
        
        if not ctx.deps.character_service:
            return {"error": "Character service not available"}
            
        # Apply healing via service
        updated_character = ctx.deps.character_service.heal(amount, source)
        
        return {
            "message": f"Healed {amount} HP from {source}",
            "current_hp": updated_character.combat_stats.current_hit_points,
            "max_hp": updated_character.combat_stats.max_hit_points
        }
        
    except Exception as e:
        log_warning("Error in character_heal", error=str(e))
        return {"error": f"Failed to heal: {str(e)}"}

def character_apply_xp(ctx: RunContext[GameSessionService], amount: int, reason: str = "milestone") -> dict:
    """
    Award experience points to the character.
    
    WHEN TO USE:
    - When the character completes a quest, defeats enemies, or reaches a milestone.
    
    Args:
        amount (int): Amount of XP to award.
        reason (str): Reason for the award. Default: "milestone".
    
    Returns:
        dict: Updated XP total.
    """
    try:
        log_debug(
            "Tool character_apply_xp called",
            tool="character_apply_xp",
            player_id=str(ctx.deps.character_id),
            amount=amount,
            reason=reason
        )
        
        if not ctx.deps.character_service:
            return {"error": "Character service not available"}
            
        # Add XP via service
        updated_character = ctx.deps.character_service.apply_xp(amount)
        
        return {
            "message": f"Gained {amount} XP for {reason}",
            "total_xp": updated_character.experience_points,
            "level": updated_character.level
        }
        
    except Exception as e:
        log_warning("Error in character_apply_xp", error=str(e))
        return {"error": f"Failed to apply XP: {str(e)}"}


