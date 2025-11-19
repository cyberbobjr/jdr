from pydantic_ai import RunContext
from back.services.game_session_service import GameSessionService
from back.utils.logger import log_debug


def inventory_add_item(ctx: RunContext[GameSessionService], item_id: str, qty: int = 1) -> dict:
    """
    Add an item to the character's inventory via EquipmentService.

    Args:
        item_id (str): Identifier of the item to acquire.
        qty (int): Quantity to add. Default: 1.

    Returns:
        dict: Summary of the updated inventory.
    """
    log_debug("Tool inventory_add_item called", tool="inventory_add_item", player_id=str(ctx.deps.character_id), item_id=item_id, qty=qty)
    
    # ✅ PATTERN CORRECT - Utilisation des services spécialisés via SessionService
    if ctx.deps.equipment_service:
        # Note: equipment_service.add_item returns the updated character
        updated_character = ctx.deps.equipment_service.add_item(ctx.deps.character_data, item_id=item_id, quantity=qty)
        # Update the session's character data
        ctx.deps.character_data = updated_character
        return {"message": f"Added {qty} x {item_id}", "inventory": [i.item_id for i in updated_character.inventory]}
    else:
        return {"error": "Equipment service not available"}


def inventory_remove_item(ctx: RunContext[GameSessionService], item_id: str, qty: int = 1) -> dict:
    """
    Remove an item from the character's inventory via EquipmentService.

    Args:
        item_id (str): Identifier of the item to remove.
        qty (int): Quantity to remove. Default: 1.

    Returns:
        dict: Summary of the updated inventory.
    """
    log_debug("Tool inventory_remove_item called", tool="inventory_remove_item", player_id=str(ctx.deps.character_id), item_id=item_id, qty=qty)
    
    # ✅ PATTERN CORRECT - Utilisation des services spécialisés via SessionService
    if ctx.deps.equipment_service:
        # Note: equipment_service.remove_item returns the updated character
        updated_character = ctx.deps.equipment_service.remove_item(ctx.deps.character_data, item_id=item_id, quantity=qty)
        # Update the session's character data
        ctx.deps.character_data = updated_character
        return {"message": f"Removed {qty} x {item_id}", "inventory": [i.item_id for i in updated_character.inventory]}
    else:
        return {"error": "Equipment service not available"}
