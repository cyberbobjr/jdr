import pytest
from uuid import uuid4
from back.tools.inventory_tools import inventory_add_item_tool

@pytest.mark.asyncio
async def test_inventory_add_item_integration():
    player_id = uuid4()
    item_id = "sword"
    qty = 1

    input_data = {"player_id": str(player_id), "item_id": item_id, "qty": qty}
    result = inventory_add_item_tool.function(player_id=str(player_id), item_id=item_id, qty=qty)
    assert "inventory" in result
    assert item_id in result["inventory"]
    assert result["inventory"][item_id] == qty
