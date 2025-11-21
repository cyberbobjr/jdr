from pydantic_ai import RunContext
from back.services.game_session_service import GameSessionService
from back.utils.logger import log_debug, log_warning


def inventory_add_item(ctx: RunContext[GameSessionService], item_id: str, qty: int = 1, cost: int = 0) -> dict:
    """
    Add an item to the character's inventory.
    
    This tool handles item acquisition with optional cost deduction.
    If cost is provided, it will be deducted from the character's gold before adding the item.
    
    Args:
        item_id (str): Identifier of the item to acquire (must be in English).
        qty (int): Quantity to add. Default: 1.
        cost (int): Cost in gold pieces to deduct. Default: 0 (free item).
    
    Returns:
        dict: Summary of the transaction with updated inventory.
    """
    try:
        log_debug(
            "Tool inventory_add_item called", 
            tool="inventory_add_item", 
            player_id=str(ctx.deps.character_id), 
            item_id=item_id, 
            qty=qty,
            cost=cost
        )
        
        # Validate item_id is in English (basic check: no accented characters)
        if any(char in item_id for char in "éèêëàâäôöûüçñ"):
            return {
                "error": f"Item ID must be in English. Received: '{item_id}'",
                "suggestion": "Use English names like 'longsword' instead of 'épée_longue'"
            }
        
        if not ctx.deps.equipment_service or not ctx.deps.character_service:
            return {"error": "Equipment or character service not available"}
        
        # Get current character
        character = ctx.deps.character_service.get_character()
        
        # Check if player can afford the item
        if cost > 0:
            if character.gold < cost:
                return {
                    "error": f"Not enough gold. Required: {cost}, Available: {character.gold}",
                    "transaction": "failed"
                }
            
            # Deduct cost
            ctx.deps.character_service.add_gold(-cost)
            log_debug(
                "Gold deducted for item purchase",
                character_id=str(ctx.deps.character_id),
                cost=cost,
                remaining_gold=character.gold - cost
            )
        
        # Add item to inventory (this also saves the character)
        updated_character = ctx.deps.equipment_service.add_item(
            ctx.deps.character_service.get_character(),
            item_id=item_id,
            quantity=qty
        )
        
        # Get updated inventory list
        inventory_items = ctx.deps.equipment_service.get_equipment_list(updated_character)
        
        result = {
            "message": f"Added {qty} x {item_id}",
            "inventory": inventory_items,
            "transaction": {
                "item": item_id,
                "quantity": qty,
                "cost": cost,
                "gold_remaining": updated_character.gold
            }
        }
        
        if cost > 0:
            result["message"] += f" for {cost} gold"
        
        return result
        
    except Exception as e:
        log_warning(
            "Error in inventory_add_item",
            error=str(e),
            character_id=str(ctx.deps.character_id),
            item_id=item_id
        )
        return {"error": f"Failed to add item: {str(e)}"}


def inventory_remove_item(ctx: RunContext[GameSessionService], item_id: str, qty: int = 1) -> dict:
    """
    Remove an item from the character's inventory.
    
    Args:
        item_id (str): Identifier of the item to remove (UUID or name).
        qty (int): Quantity to remove. Default: 1.
    
    Returns:
        dict: Summary of the updated inventory.
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
        
        # Remove item (this also saves the character)
        updated_character = ctx.deps.equipment_service.remove_item(
            character,
            item_id=item_id,
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
    
    This tool allows the LLM to query what items are available in the game,
    ensuring that proposed items are consistent with the game rules.
    
    Args:
        category (str): Category to filter by. Options: "weapons", "armor", "accessories", "consumables", "all". Default: "all".
    
    Returns:
        dict: List of available items with their item_id, name, cost, and description.
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
                    "cost": int(item["cost"]),
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

