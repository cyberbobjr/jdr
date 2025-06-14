from back.services.character_service import CharacterService
from back.models.schema import Character
import json
import uuid

def test_get_all_characters(isolated_data_dir):
    # Création d'un personnage strictement conforme au modèle métier, sans accents dans les clés
    character_id = uuid.uuid4()
    characters_dir = isolated_data_dir / "characters"
    characters_dir.mkdir(exist_ok=True)
    item = {
        "id": "sword_001",
        "name": "Epee courte",
        "item_type": "Arme",
        "price_pc": 100,
        "weight_kg": 2.5,
        "description": "Une epee courte standard.",
        "category": "Epee",
        "damage": "1d6+1",
        "protection": None,
        "armor_type": None,
        "quantity": 1,
        "is_equipped": True,
        "crafting_time": None,
        "special_properties": None
    }
    state = {
        "id": str(character_id),
        "name": "Test Hero",
        "race": "Humain",
        "culture": "Rurale",
        "profession": "Aventurier",
        "caracteristiques": {
            "Force": 10,
            "Constitution": 10,
            "Agilite": 10,
            "Rapidite": 10,
            "Volonte": 10,
            "Raisonnement": 10,
            "Intuition": 10,
            "Presence": 10
        },
        "competences": {"Athletisme": 5},
        "hp": 42,
        "xp": 0,
        "gold": 0,
        "inventory": [item],
        "spells": [],
        "equipment_summary": {"total_weight": 2.5, "total_value": 100.0, "remaining_gold": 0.0},
        "culture_bonuses": {"Endurance": 1}
    }
    character_data = {"state": state}
    (characters_dir / f"{character_id}.json").write_text(json.dumps(character_data), encoding="utf-8")
    characters = CharacterService.get_all_characters()
    assert isinstance(characters, list)
    assert len(characters) > 0
    assert isinstance(characters[0], Character)
    assert hasattr(characters[0], "inventory")
    assert not hasattr(characters[0], "equipment")
    assert hasattr(characters[0], "spells")
    assert hasattr(characters[0], "equipment_summary")
    assert hasattr(characters[0], "culture_bonuses")
    if characters[0].inventory:
        from back.models.schema import Item
        assert isinstance(characters[0].inventory[0], Item)
