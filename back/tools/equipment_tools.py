from pydantic_ai import RunContext
from back.services.game_session_service import GameSessionService
from back.utils.logger import log_debug, log_warning


def inventory_add_item(ctx: RunContext[GameSessionService], item_id: str, qty: int = 1) -> dict:
    """
    Add a free item to the character's inventory.

    This tool adds an item to the character's inventory without any cost.
    It should be used for rewards, loot, gifts, or quest items found during the game.
    This action persists the changes to the character's state.
    WHEN NOT TO USE:
    - DO NOT use this for purchases - use `inventory_buy_item` instead
    
    Args:
        item_id (str): The unique identifier of the item to acquire (must be in English).
        qty (int): The quantity of the item to add. Must be a positive integer. Default is 1.

    Returns:
        dict: A dictionary containing a success message and the updated inventory list.
    """
    try:
        log_debug(
            "Tool inventory_add_item called", 
            tool="inventory_add_item", 
            player_id=str(ctx.deps.character_id), 
            item_id=item_id, 
            qty=qty
        )
        
        # Validate item_id is in English (basic check: no accented characters)
        if any(char in item_id for char in "éèêëàâäôöûüçñ"):
            return {
                "error": f"Item ID must be in English. Received: '{item_id}'",
                "suggestion": "Use English names like 'longsword' instead of 'épée_longue'"
            }
        
        if not ctx.deps.equipment_service or not ctx.deps.character_service:
            return {"error": "Equipment or character service not available"}
        
        # Add item to inventory (this also saves the character)
        updated_character = ctx.deps.equipment_service.add_item(
            ctx.deps.character_service.get_character(),
            item_id=item_id,
            quantity=qty
        )
        
        # Get updated inventory list
        inventory_items = ctx.deps.equipment_service.get_equipment_list(updated_character)
        
        return {
            "message": f"Added {qty} x {item_id}",
            "inventory": inventory_items
        }
        
    except Exception as e:
        log_warning(
            "Error in inventory_add_item",
            error=str(e),
            character_id=str(ctx.deps.character_id),
            item_id=item_id
        )
        return {"error": f"Failed to add item: {str(e)}"}


def inventory_buy_item(
    ctx: RunContext[GameSessionService], 
    item_id: str, 
    qty: int = 1
) -> dict:
    """
    Purchase an item and add it to the character's inventory.

    This tool handles item purchases by deducting the cost from the character's currency.
    It should be used when the character buys an item from a shop or merchant.
    It automatically checks affordability and performs currency conversion if necessary.

    Args:
        item_id (str): The unique identifier of the item to purchase (must be in English, from equipment database).
        qty (int): The quantity of the item to purchase. Must be a positive integer. Default is 1.

    Returns:
        dict: A dictionary containing the transaction details, updated inventory, and remaining currency.
              Returns an error if the item is not found or funds are insufficient.
    """
    try:
        log_debug(
            "Tool inventory_buy_item called", 
            tool="inventory_buy_item", 
            player_id=str(ctx.deps.character_id), 
            item_id=item_id, 
            qty=qty
        )
        
        if not ctx.deps.equipment_service or not ctx.deps.character_service:
            return {"error": "Equipment or character service not available"}
            
        # Get item details to check cost
        item_data = ctx.deps.equipment_service.equipment_manager.get_equipment_by_id(item_id)
        if not item_data:
            return {"error": f"Item not found: {item_id}"}
            
        cost_gold = item_data.get("cost_gold", 0) * qty
        cost_silver = item_data.get("cost_silver", 0) * qty
        cost_copper = item_data.get("cost_copper", 0) * qty
        
        # Get current character
        character = ctx.deps.character_service.get_character()
        
        # Check affordability
        if not character.equipment.can_afford(cost_gold, cost_silver, cost_copper):
            total_cost_copper = (cost_gold * 100) + (cost_silver * 10) + cost_copper
            current_copper = character.equipment.get_total_in_copper()
            return {
                "error": f"Insufficient funds. Cost: {cost_gold}G {cost_silver}S {cost_copper}C (Total: {total_cost_copper}C). Available: {current_copper}C",
                "transaction": "failed"
            }
            
        # Deduct currency
        if not character.equipment.deduct_currency(cost_gold, cost_silver, cost_copper):
             return {"error": "Transaction failed during currency deduction"}
             
        # Add item
        updated_character = ctx.deps.equipment_service.add_item(
            character,
            item_id=item_id,
            quantity=qty
        )
        
        # Get updated inventory list
        inventory_items = ctx.deps.equipment_service.get_equipment_list(updated_character)
        
        return {
            "message": f"Purchased {qty} x {item_id} for {cost_gold}G {cost_silver}S {cost_copper}C",
            "inventory": inventory_items,
            "transaction": {
                "item": item_id,
                "quantity": qty,
                "cost": {"gold": cost_gold, "silver": cost_silver, "copper": cost_copper},
                "currency_remaining": {
                    "gold": updated_character.gold,
                    "silver": updated_character.silver,
                    "copper": updated_character.copper
                }
            }
        }
        
    except Exception as e:
        log_warning(
            "Error in inventory_buy_item",
            error=str(e),
            character_id=str(ctx.deps.character_id),
            item_id=item_id
        )
        return {"error": f"Failed to buy item: {str(e)}"}


def inventory_remove_item(ctx: RunContext[GameSessionService], item_id: str, qty: int = 1) -> dict:
    """
    Remove an item from the character's inventory.

    This tool removes a specified quantity of an item from the character's inventory.
    It should be used when an item is consumed, lost, sold, or given away.
    This action persists the changes to the character's state.

    Args:
        item_id (str): The unique identifier or name of the item to remove.
        qty (int): The quantity of the item to remove. Must be a positive integer. Default is 1.

    Returns:
        dict: A dictionary containing a success message and the updated inventory list.
    """
    try:
        log_debug(
            "Tool inventory_remove_item called", 
            tool="inventory_remove_item", 
            player_id=str(ctx.deps.character_id), 
            item_id=item_id, 
            qty=qty
        )
        
        if not ctx.deps.equipment_service or not ctx.deps.character_service:
            return {"error": "Equipment or character service not available"}
        
        # Get current character
        character = ctx.deps.character_service.get_character()
        
        # Resolve item_id if it's a name
        target_id = item_id
        # Simple check: if it doesn't look like a UUID (len 36), try to find by name
        if len(item_id) != 36:
            found_item = None
            all_items = ctx.deps.equipment_service.get_equipment_details(character)
            for item in all_items:
                if item.name.lower() == item_id.lower() or item.id == item_id:
                    found_item = item
                    break
            
            if found_item:
                target_id = found_item.id
            else:
                # If not found by name, maybe it's a partial match or just not there.
                # Let the service handle it (it will fail silently if not found by ID)
                # But we can return a better error here
                return {"error": f"Item '{item_id}' not found in inventory."}

        # Remove item (this also saves the character)
        updated_character = ctx.deps.equipment_service.remove_item(
            character,
            item_id=target_id,
            quantity=qty
        )
        
        # Get updated inventory list
        inventory_items = ctx.deps.equipment_service.get_equipment_list(updated_character)
        
        return {
            "message": f"Removed {qty} x {item_id}",
            "inventory": inventory_items
        }
        
    except Exception as e:
        log_warning(
            "Error in inventory_remove_item",
            error=str(e),
            character_id=str(ctx.deps.character_id),
            item_id=item_id
        )
        return {"error": f"Failed to remove item: {str(e)}"}


def list_available_equipment(ctx: RunContext[GameSessionService], category: str = "all") -> dict:
    """
    List available equipment items by category.

    This tool retrieves a list of equipment items available in the game, filtered by category.
    It should be used to check item availability, costs, and stats before making a purchase or rewarding loot.
    This does not modify any state.

    Args:
        category (str): The category to filter by. Options: "weapons", "armor", "accessories", "consumables", "all". Default is "all".

    Returns:
        dict: A dictionary containing the list of available items with their details (id, name, cost, description, stats).
    """
    try:
        log_debug(
            "Tool list_available_equipment called",
            tool="list_available_equipment",
            player_id=str(ctx.deps.character_id),
            category=category
        )
        
        if not ctx.deps.equipment_service:
            return {"error": "Equipment service not available"}
        
        # Get equipment manager from the service
        equipment_manager = ctx.deps.equipment_service.equipment_manager
        
        # Get all equipment organized by categories
        all_equipment = equipment_manager.get_all_equipment()
        
        # Normalize category input
        category_lower = category.lower().strip()
        
        # Filter by category if specified
        if category_lower == "all":
            categories_to_show = all_equipment
        elif category_lower in all_equipment:
            categories_to_show = {category_lower: all_equipment[category_lower]}
        else:
            return {
                "error": f"Invalid category: '{category}'. Valid options: weapons, armor, accessories, consumables, all"
            }
        
        # Format the response
        result = {
            "category_filter": category,
            "items": {}
        }
        
        for cat_name, items_list in categories_to_show.items():
            formatted_items = []
            for item in items_list:
                formatted_items.append({
                    "item_id": item["id"],
                    "name": item["name"],
                    "cost": {
                        "gold": item.get("cost_gold", 0),
                        "silver": item.get("cost_silver", 0),
                        "copper": item.get("cost_copper", 0)
                    },
                    "description": item.get("description", "No description available"),
                    "weight": item.get("weight", 0),
                    # Include category-specific info
                    **({"damage": item["damage"]} if "damage" in item else {}),
                    **({"protection": item["protection"]} if "protection" in item else {}),
                    **({"range": item["range"]} if "range" in item else {})
                })
            
            result["items"][cat_name] = formatted_items
        
        # Add summary
        total_items = sum(len(items) for items in result["items"].values())
        result["summary"] = f"Found {total_items} items in {len(result['items'])} categories"
        
        return result
        
    except Exception as e:
        log_warning(
            "Error in list_available_equipment",
            error=str(e),
            character_id=str(ctx.deps.character_id),
            category=category
        )
        return {"error": f"Failed to list equipment: {str(e)}"}

