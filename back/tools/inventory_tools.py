from pydantic_ai import RunContext
from ..services.inventory_service import InventoryService
from back.services.session_service import SessionService
from back.utils.logger import log_debug

svc = InventoryService()

def inventory_add_item(ctx: RunContext[SessionService], item_id: str, qty: int = 1) -> dict:
    """
    Ajoute un objet à l'inventaire du personnage.

    Args:
        item_id (str): Identifiant de l'objet à acquérir. Ex. : 'épée_longue'.
        qty (int): Quantité à ajouter. Par défaut : 1.
    
    Returns:
        dict: Résumé de l'inventaire mis à jour.
    """
    log_debug("Tool inventory_add_item appelé", tool="inventory_add_item", player_id=str(ctx.deps.character_id), item_id=item_id, qty=qty)
    summary = svc.add_item(player_id=ctx.deps.character_id, item_id=item_id, qty=qty)
    return summary

# Tool definition removed - now handled directly by PydanticAI agent

def inventory_remove_item(ctx: RunContext[SessionService], item_id: str, qty: int = 1) -> dict:
    """
    Retire un objet de l'inventaire du personnage.

    Args:
        item_id (str): Identifiant de l'objet à retirer. Ex. : 'épée_longue'.
        qty (int): Quantité à retirer. Par défaut : 1.
    
    Returns:
        dict: Résumé de l'inventaire mis à jour.
    """
    log_debug("Tool inventory_remove_item appelé", tool="inventory_remove_item", player_id=str(ctx.deps.character_id), item_id=item_id, qty=qty)
    summary = svc.remove_item(player_id=ctx.deps.character_id, item_id=item_id, qty=qty)
    return summary

# Tool definition removed - now handled directly by PydanticAI agent
