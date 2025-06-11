from back.services.character_service import CharacterService
from back.models.schema import Character

def test_get_all_characters(isolated_data_dir):
    characters = CharacterService.get_all_characters()
    assert isinstance(characters, list)
    assert len(characters) > 0
    assert isinstance(characters[0], Character)
    # Vérifie que l'ancien champ equipment a été remplacé par inventory
    assert hasattr(characters[0], "inventory")
    assert not hasattr(characters[0], "equipment")  # L'ancien champ ne devrait plus exister
    assert hasattr(characters[0], "spells")
    assert hasattr(characters[0], "equipment_summary")
    assert hasattr(characters[0], "culture_bonuses")
    # Vérifie que l'inventaire contient des objets Item
    if characters[0].inventory:
        from back.models.schema import Item
        assert isinstance(characters[0].inventory[0], Item)
