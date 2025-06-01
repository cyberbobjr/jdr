import pytest
from uuid import uuid4
from back.services.inventory_service import InventoryService

@pytest.fixture
def inventory_service():
    return InventoryService()

def test_add_item(inventory_service):
    player_id = uuid4()
    result = inventory_service.add_item(player_id, "sword", 1)
    assert "inventory" in result

def test_remove_item(inventory_service):
    player_id = uuid4()
    result = inventory_service.remove_item(player_id, "sword", 1)
    assert "inventory" in result

def test_equip_item(inventory_service):
    player_id = uuid4()
    result = inventory_service.equip_item(player_id, "sword")
    assert "equipped" in result

def test_unequip_item(inventory_service):
    player_id = uuid4()
    result = inventory_service.unequip_item(player_id, "sword")
    assert "equipped" in result
