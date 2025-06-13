import pytest
from back.services.character_service import CharacterService

@pytest.fixture
def character_service():
    # Utiliser un personnage existant pour les tests
    return CharacterService("79e55c14-7dd5-4189-b209-ea88f6d067eb")

def test_add_item(character_service):
    result = character_service.add_item("sword", 1)
    assert "inventory" in result

def test_remove_item(character_service):
    result = character_service.remove_item("sword", 1)
    assert "inventory" in result

def test_equip_item(character_service):
    result = character_service.equip_item("sword")
    assert "inventory" in result

def test_unequip_item(character_service):
    result = character_service.unequip_item("sword")
    assert "inventory" in result

def test_inventory_workflow(character_service):
    """Test du workflow complet d'inventaire"""
    # Ajouter un objet
    result = character_service.add_item("test_item", 2)
    assert "inventory" in result
    
    # Équiper l'objet
    result = character_service.equip_item("test_item")
    assert "inventory" in result
    
    # Déséquiper l'objet
    result = character_service.unequip_item("test_item")
    assert "inventory" in result
    
    # Retirer l'objet
    result = character_service.remove_item("test_item", 2)
    assert "inventory" in result
