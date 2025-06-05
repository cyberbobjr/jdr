from uuid import UUID
from ..services.inventory_service import InventoryService
from back.utils.logger import log_debug

svc = InventoryService()

def inventory_add_item(player_id: UUID, item_id: str, qty: int = 1) -> dict:
    """
    ### inventory_add_item
    **Description :** Ajoute un objet à l'inventaire puis renvoie le résumé de l'inventaire mis à jour.
    **Paramètres :**
    - `player_id` (UUID) : Identifiant du joueur
    - `item_id` (str) : Identifiant de l'objet à acquérir
    - `qty` (int) : Quantité à ajouter (défaut 1)
    **Retour :**
    - (dict) : Résumé de l'inventaire mis à jour.
    """
    log_debug("Tool inventory_add_item appelé", tool="inventory_add_item", player_id=str(player_id), item_id=item_id, qty=qty)
    summary = svc.add_item(player_id=player_id, item_id=item_id, qty=qty)
    return summary

# Tool definition removed - now handled directly by PydanticAI agent

def inventory_remove_item(player_id: UUID, item_id: str, qty: int = 1) -> dict:
    """
    ### inventory_remove_item
    **Description :** Retire un objet de l'inventaire puis renvoie le résumé de l'inventaire mis à jour.
    **Paramètres :**
    - `player_id` (UUID) : Identifiant du joueur
    - `item_id` (str) : Identifiant de l'objet à retirer
    - `qty` (int) : Quantité à retirer (défaut 1)
    **Retour :**
    - (dict) : Résumé de l'inventaire mis à jour.
    """
    log_debug("Tool inventory_remove_item appelé", tool="inventory_remove_item", player_id=str(player_id), item_id=item_id, qty=qty)
    summary = svc.remove_item(player_id=player_id, item_id=item_id, qty=qty)
    return summary

# Tool definition removed - now handled directly by PydanticAI agent
