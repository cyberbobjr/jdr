from pydantic_ai import RunContext
from back.services.session_service import SessionService
from back.utils.logger import log_debug


def inventory_add_item(ctx: RunContext[SessionService], item_id: str, qty: int = 1) -> dict:
    """
    Add an item to the character's inventory via EquipmentService.

    Args:
        item_id (str): Identifier of the item to acquire.
        qty (int): Quantity to add. Default: 1.

    Returns:
        dict: Summary of the updated inventory.
    """
    log_debug("Tool inventory_add_item called", tool="inventory_add_item", player_id=str(ctx.deps.character_id), item_id=item_id, qty=qty)
    if ctx.deps.character_service:
        return ctx.deps.character_service.add_item(item_id=item_id, qty=qty)
    else:
        return {"error": "Character service not available"}


def inventory_remove_item(ctx: RunContext[SessionService], item_id: str, qty: int = 1) -> dict:
    """
    Remove an item from the character's inventory via EquipmentService.

    Args:
        item_id (str): Identifier of the item to remove.
        qty (int): Quantity to remove. Default: 1.

    Returns:
        dict: Summary of the updated inventory.
    """
    log_debug("Tool inventory_remove_item called", tool="inventory_remove_item", player_id=str(ctx.deps.character_id), item_id=item_id, qty=qty)
    if ctx.deps.character_service:
        return ctx.deps.character_service.remove_item(item_id=item_id, qty=qty)
    else:
        return {"error": "Character service not available"}
