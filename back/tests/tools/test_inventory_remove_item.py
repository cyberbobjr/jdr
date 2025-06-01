import pytest
from uuid import uuid4
from back.tools.inventory_tools import inventory_remove_item_tool

@pytest.mark.asyncio
async def test_inventory_remove_item_integration():
    player_id = uuid4()
    item_id = "sword"
    qty = 1
    # Ajout préalable pour garantir la présence de l'objet
    from back.tools.inventory_tools import inventory_add_item_tool
    inventory_add_item_tool.function(player_id=str(player_id), item_id=item_id, qty=qty)
    # Test suppression
    result = inventory_remove_item_tool.function(player_id=str(player_id), item_id=item_id, qty=qty)
    assert "inventory" in result
    assert item_id not in result["inventory"] or result["inventory"][item_id] == 0
