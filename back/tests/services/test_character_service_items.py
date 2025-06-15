from back.services.character_service import CharacterService
from back.models.schema import Item
import uuid
import json
from back.models.schema import Item

def create_test_character(character_id, data_dir):
    """
    Crée un personnage minimal pour les tests dans le dossier isolé.
    """
    character_data = {
        "id": character_id,
        "name": "Test Hero",
        "race": "Humain",
        "culture": "Rurale",
        "profession": "Aventurier",
        "caracteristiques": {"Force": 10},
        "competences": {},
        "hp": 42,
        "xp": 0,
        "gold": 0,
        "inventory": [],
        "spells": [],
        "equipment_summary": {},
        "culture_bonuses": {}
    }
    characters_dir = data_dir / "characters"
    characters_dir.mkdir(exist_ok=True)
    (characters_dir / f"{character_id}.json").write_text(json.dumps(character_data), encoding="utf-8")


def test_item_exists_false(isolated_data_dir):
    character_id = str(uuid.uuid4())
    create_test_character(character_id, isolated_data_dir)
    service = CharacterService(character_id)
    service.character_data.inventory = []
    assert not service.item_exists("test_id")

def test_item_exists_true(isolated_data_dir):
    character_id = str(uuid.uuid4())
    create_test_character(character_id, isolated_data_dir)
    service = CharacterService(character_id)
    item = Item(id="test_id", name="Test", item_type="Materiel", price_pc=0, weight_kg=0, description="", quantity=1)
    service.character_data.inventory = [item]
    assert service.item_exists("test_id")

def test_add_item_object(isolated_data_dir):
    character_id = str(uuid.uuid4())
    create_test_character(character_id, isolated_data_dir)
    service = CharacterService(character_id)
    item = Item(id="item1", name="Test", item_type="Materiel", price_pc=0, weight_kg=0, description="", quantity=2)
    service.character_data.inventory = []
    result = service.add_item_object(item)
    assert any(i["id"] == "item1" for i in result["inventory"])

def test_instantiate_item_by_id(isolated_data_dir):
    character_id = str(uuid.uuid4())
    create_test_character(character_id, isolated_data_dir)
    service = CharacterService(character_id)
    item = service.instantiate_item_by_id("Coutelas", qty=2)
    assert item.name == "Coutelas"
    assert item.quantity == 2

def test_add_item_instantiates(isolated_data_dir):
    character_id = str(uuid.uuid4())
    create_test_character(character_id, isolated_data_dir)
    service = CharacterService(character_id)
    service.character_data.inventory = []
    result = service.add_item("Coutelas", qty=3)
    assert any(i["name"] == "Coutelas" and i["quantity"] == 3 for i in result["inventory"])
