# Ajouter les imports nécessaires pour les tests FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, AsyncMock
from back.app import app
from back.models.domain.character_v2 import CharacterV2, Stats, Skills, CombatStats, Equipment, Spells, CharacterStatus
from back.models.schema import RaceData, CultureData
from uuid import uuid4
from datetime import datetime

client = TestClient(app)

# Mock data for managers
MOCK_RACES_DATA = [
    RaceData(
        id="humans",
        name="Humans",
        characteristic_bonuses={"Willpower": 1},
        base_languages=["Westron"],
        optional_languages=["Sindarin"],
        cultures=[
            CultureData(id="gondorians", name="Gondorians", skill_bonuses={"General Knowledge": 1}, traits="Tradition and pride")
        ]
    )
]

MOCK_SKILLS_DATA = {
    "skill_groups": {
        "combat": {
            "name": "Combat",
            "skills": {
                "melee_weapons": {
                    "id": "melee_weapons",
                    "name": "Melee Weapons",
                    "description": "Proficiency with close-quarters weapons like swords, axes, and spears.",
                    "stat_bonuses": {
                        "strength": {
                            "min_value": 14,
                            "bonus_points": 3
                        }
                    }
                }
            }
        }
    },
    "racial_affinities": {
        "Noldor": [
            {"skill": "crafting", "base_points": 3}
        ]
    }
}

MOCK_EQUIPMENT_DATA = {
    "weapons": [
        {
            "id": "longsword",
            "name": "Longsword",
            "category": "weapon",
            "cost": 2.0,
            "weight": 1.5,
            "quantity": 1,
            "equipped": False,
            "damage": "1d8+4",
            "description": "Balanced and versatile one-handed sword",
            "range": "150"
        }
    ],
    "armor": [],
    "accessories": [],
    "consumables": []
}

MOCK_STATS_DATA = {
    "stats": {
        "strength": {
            "id": "strength",
            "name": "Strength",
            "description": "Physical strength, build. Determines melee damage and carrying capacity.",
            "min_value": 3,
            "max_value": 20
        }
    },
    "value_range": {"min": 3, "max": 20},
    "bonus_formula": "(value - 10) // 2",
    "bonus_table": {},
    "cost_table": {},
    "starting_points": None
}

@patch('back.routers.creation.RacesManager')
def test_get_races(mock_races_manager):
    mock_races_manager_instance = mock_races_manager.return_value
    mock_races_manager_instance.get_all_races.return_value = MOCK_RACES_DATA
    
    response = client.get("/api/creation/races")
    assert response.status_code == 200
    assert response.json() == [race.model_dump() for race in MOCK_RACES_DATA]

@patch('back.routers.creation.UnifiedSkillsManager')
def test_get_skills(mock_skills_manager):
    mock_skills_manager_instance = mock_skills_manager.return_value
    mock_skills_manager_instance.get_all_data.return_value = MOCK_SKILLS_DATA

    response = client.get("/api/creation/skills")
    assert response.status_code == 200
    assert response.json() == MOCK_SKILLS_DATA

@patch('back.routers.creation.EquipmentManager')
def test_get_equipment(mock_equipment_manager):
    mock_equipment_manager_instance = mock_equipment_manager.return_value
    mock_equipment_manager_instance.get_all_equipment.return_value = MOCK_EQUIPMENT_DATA

    response = client.get("/api/creation/equipment")
    assert response.status_code == 200
    data = response.json()
    # Check that the structure is correct
    assert "weapons" in data
    assert "armor" in data
    assert "accessories" in data
    assert "consumables" in data
    assert isinstance(data["weapons"], list)
    if data["weapons"]:
        item = data["weapons"][0]
        assert "id" in item
        assert "name" in item
        assert "category" in item
        assert "cost" in item
        assert "weight" in item
        assert "quantity" in item
        assert "equipped" in item
        assert "range" in item
        assert isinstance(item["range"], str)  # Should be string

def test_get_equipment_canonical_schema():
    """
    Ensure the equipment endpoint returns standardized categories and item keys.
    This uses the real EquipmentManager and YAML file.
    """
    response = client.get("/api/creation/equipment")
    assert response.status_code == 200
    data = response.json()
    # Categories present
    assert isinstance(data, dict)
    for key in ("weapons", "armor", "accessories", "consumables"):
        assert key in data
        assert isinstance(data[key], list)
    # At least check first weapon if exists has canonical keys
    def assert_item_schema(item: dict):
        required = {"id", "name", "category", "cost", "weight", "quantity", "equipped"}
        assert required.issubset(item.keys())
    for category in ("weapons", "armor", "accessories", "consumables"):
        if data[category]:
            assert_item_schema(data[category][0])

@patch('back.routers.creation.StatsManager')
def test_get_stats(mock_stats_manager):
    mock_stats_manager_instance = mock_stats_manager.return_value
    mock_stats_manager_instance.get_all_stats_data.return_value = MOCK_STATS_DATA
    
    response = client.get("/api/creation/stats")
    assert response.status_code == 200
    assert response.json() == MOCK_STATS_DATA

@patch('back.routers.creation.CharacterPersistenceService')
@patch('back.routers.creation.RacesManager')
def test_create_character_v2_success(mock_races_manager, mock_persistence_service):
    mock_races_manager_instance = mock_races_manager.return_value
    mock_races_manager_instance.get_race_by_id.return_value = MOCK_RACES_DATA[0] # Return a valid race
    
    mock_persistence_service.save_character_data.return_value = None # Mock save operation
    
    request_data = {
        "name": "Test Character",
        "race_id": "humans",
        "culture_id": "gondorians",
        "stats": {"strength": 10, "constitution": 10, "agility": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "skills": {"combat": {"Melee Weapons": 1}},
        "physical_description": "Tall and swift"
    }
    
    response = client.post("/api/creation/create", json=request_data)
    assert response.status_code == 200
    response_data = response.json()
    assert "character_id" in response_data
    assert response_data["status"] == "created"
    assert "created_at" in response_data
    
    mock_persistence_service.save_character_data.assert_called_once()

@patch('back.routers.creation.CharacterPersistenceService')
@patch('back.routers.creation.RacesManager')
def test_create_character_v2_physical_description_persisted(mock_races_manager, mock_persistence_service):
    mock_races_manager_instance = mock_races_manager.return_value
    mock_races_manager_instance.get_race_by_id.return_value = MOCK_RACES_DATA[0]

    # Capture saved data
    saved_store = {}
    def save_side_effect(cid, data):
        saved_store['id'] = cid
        saved_store['data'] = data
        return None
    mock_persistence_service.save_character_data.side_effect = save_side_effect

    request_data = {
        "name": "Phys Desc",
        "race_id": "humans",
        "culture_id": "gondorians",
        "stats": {"strength": 10, "constitution": 10, "agility": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "skills": {"combat": {"Melee Weapons": 1}},
        "physical_description": "Scar over left eye"
    }

    resp = client.post("/api/creation/create", json=request_data)
    assert resp.status_code == 200
    char_id = resp.json()["character_id"]

    # Mock load to return last saved
    mock_persistence_service.load_character_data.return_value = saved_store['data']
    get_resp = client.get(f"/api/creation/character/{char_id}")
    assert get_resp.status_code == 200
    body = get_resp.json()
    assert body["character"]["physical_description"] == "Scar over left eye"

@patch('back.routers.creation.CharacterPersistenceService')
@patch('back.routers.creation.RacesManager')
def test_create_character_v2_invalid_race(mock_races_manager, mock_persistence_service):
    # Simuler une exception HTTPException en utilisant ValueError
    mock_races_manager_instance = mock_races_manager.return_value
    # Instead of raising HTTPException, we'll make the mock return None and let the router raise the exception
    mock_races_manager_instance.get_race_by_id.return_value = None
    
    request_data = {
        "name": "Test Character",
        "race_id": "invalid_race",
        "culture_id": "gondorians",
        "stats": {"strength": 10, "constitution": 10, "agility": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "skills": {"combat": {"Melee Weapons": 1}}
    }
    
    response = client.post("/api/creation/create", json=request_data)
    assert response.status_code == 404
    assert "Race with id 'invalid_race' not found" in response.json()["detail"]
    mock_persistence_service.save_character_data.assert_not_called()

@patch('back.routers.creation.CharacterPersistenceService')
def test_update_character_v2_success(mock_persistence_service):
    character_id = uuid4()
    existing_character_data = CharacterV2(
        id=character_id,
        name="Old Name",
        race="humans",
        culture="gondorians",
        stats=Stats(
            strength=10,
            constitution=10,
            agility=10,
            intelligence=10,
            wisdom=10,
            charisma=10
        ),
        skills=Skills(
            combat={
                "Melee Weapons": 1
            }
        ),
        combat_stats=CombatStats(
            max_hit_points=50,
            current_hit_points=50,
            max_mana_points=30,
            current_mana_points=30,
            armor_class=10,
            attack_bonus=0
        ),
        equipment=Equipment(
            weapons=[],
            armor=[],
            accessories=[],
            consumables=[],
            gold=0
        ),
        spells=Spells(
            known_spells=[],
            spell_slots={},
            spell_bonus=0
        ),
        level=1,
        status=CharacterStatus.DRAFT,
        experience_points=0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        description=None
    ).model_dump()
    
    mock_persistence_service.load_character_data.return_value = existing_character_data
    mock_persistence_service.save_character_data.return_value = existing_character_data  # Return the updated data
    
    update_data = {
        "character_id": str(character_id),
        "name": "New Name",
        "stats": {
            "strength": 12,
            "constitution": 10,
            "agility": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        },
        "skills": {"combat": {"Melee Weapons": 1}},
        "background": "Updated background",
        "physical_description": "Changed appearance"
    }
    
    response = client.post("/api/creation/update", json=update_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "updated"
    assert response_data["character"]["name"] == "New Name"
    assert response_data["character"]["stats"]["strength"] == 12
    assert response_data["character"]["physical_description"] == "Changed appearance"
    mock_persistence_service.save_character_data.assert_called_once()

@patch('back.routers.creation.CharacterPersistenceService')
def test_update_character_v2_not_found(mock_persistence_service):
    character_id = str(uuid4())
    mock_persistence_service.load_character_data.return_value = None
    
    update_data = {
        "character_id": character_id,
        "name": "New Name"
    }
    
    response = client.post("/api/creation/update", json=update_data)
    assert response.status_code == 404
    assert f"Character with id '{character_id}' not found" in response.json()["detail"]
    mock_persistence_service.save_character_data.assert_not_called()

@patch('back.routers.creation.CharacterPersistenceService')
def test_get_character_v2_success(mock_persistence_service):
    character_id = uuid4()
    character_data = CharacterV2(
        id=character_id,
        name="Test Character",
        race="humans",
        culture="gondorians",
        stats=Stats(strength=10, constitution=10, agility=10, intelligence=10, wisdom=10, charisma=10),
        skills=Skills(combat={"Melee Weapons": 1}),
        combat_stats=CombatStats(max_hit_points=50, current_hit_points=50, max_mana_points=30, current_mana_points=30, armor_class=10, attack_bonus=0),
        equipment=Equipment(weapons=[], armor=[], accessories=[], consumables=[], gold=0),
        spells=Spells(known_spells=[], spell_slots={}, spell_bonus=0),
        level=1,
        status=CharacterStatus.DRAFT,
        experience_points=0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        description=None
    ).model_dump()
    
    mock_persistence_service.load_character_data.return_value = character_data
    
    response = client.get(f"/api/creation/character/{character_id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "loaded"
    assert response_data["character"]["id"] == str(character_id)

@patch('back.routers.creation.CharacterPersistenceService')
def test_get_character_v2_not_found(mock_persistence_service):
    character_id = str(uuid4())
    mock_persistence_service.load_character_data.return_value = None
    
    response = client.get(f"/api/creation/character/{character_id}")
    assert response.status_code == 404
    assert f"Character with id '{character_id}' not found" in response.json()["detail"]

@patch('back.routers.creation.CharacterPersistenceService')
def test_delete_character_v2_success(mock_persistence_service):
    character_id = str(uuid4())
    mock_persistence_service.load_character_data.return_value = {"id": character_id} # Character exists
    mock_persistence_service.delete_character_data.return_value = None
    
    response = client.delete(f"/api/creation/character/{character_id}")
    assert response.status_code == 204
    mock_persistence_service.delete_character_data.assert_called_once_with(character_id)

@patch('back.routers.creation.CharacterPersistenceService')
def test_delete_character_v2_not_found(mock_persistence_service):
    character_id = str(uuid4())
    mock_persistence_service.load_character_data.return_value = None
    
    response = client.delete(f"/api/creation/character/{character_id}")
    assert response.status_code == 404
    assert f"Character with id '{character_id}' not found" in response.json()["detail"]
    mock_persistence_service.delete_character_data.assert_not_called()

def test_validate_character_v2_success():
    valid_character_data = {
        "id": str(uuid4()),
        "name": "Valid Character",
        "race": "humans",
        "culture": "gondorians",
        "stats": {"strength": 10, "constitution": 10, "agility": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "skills": {"combat": {"Melee Weapons": 1}},
        "combat_stats": {"max_hit_points": 50, "current_hit_points": 50, "max_mana_points": 30, "current_mana_points": 30, "armor_class": 10, "attack_bonus": 0},
        "equipment": {"weapons": [], "armor": [], "accessories": [], "consumables": [], "gold": 0},
        "spells": {"known_spells": [], "spell_slots": {}, "spell_bonus": 0},
        "level": 1,
        "status": "draft",
        "experience_points": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "description": None
    }

    response = client.post("/api/creation/validate-character", json=valid_character_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["valid"] is True
    assert response_data["message"] == "Character is valid"
    assert "character" in response_data

def test_validate_character_v2_failure():
    invalid_character_data = {
        "id": str(uuid4()),
        "name": "Invalid Character",
        "race": "humans",
        "culture": "gondorians",
        "stats": {"strength": "not_an_int"}, # Invalid stat
        "skills": {"combat": {"Melee Weapons": 1}},
        "combat_stats": {"max_hit_points": 50, "current_hit_points": 50, "max_mana_points": 30, "current_mana_points": 30, "armor_class": 10, "attack_bonus": 0},
        "equipment": {"weapons": [], "armor": [], "accessories": [], "consumables": [], "gold": 0},
        "spells": {"known_spells": [], "spell_slots": {}, "spell_bonus": 0},
        "level": 1,
        "status": "draft",
        "experience_points": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "description": None
    }

    response = client.post("/api/creation/validate-character", json=invalid_character_data)
    assert response.status_code == 422 # FastAPI returns 422 for Pydantic validation errors
    response_data = response.json()
    assert "detail" in response_data
    # Check that it's a validation error about the strength field being a string instead of int
    assert any("strength" in str(error) and ("int" in str(error) or "integer" in str(error)) for error in response_data["detail"])


def test_get_stats_integration_range_and_formula():
    """
    Integration test (no mocks): ensure /stats exposes the simplified 3–20 model.
    """
    resp = client.get("/api/creation/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "value_range" in data
    assert data["value_range"]["min"] == 3
    assert data["value_range"]["max"] == 20
    assert "bonus_formula" in data
    assert data["bonus_formula"] == "(value - 10) // 2"


@patch('back.routers.creation.CharacterPersistenceService')
@patch('back.routers.creation.RacesManager')
def test_create_character_v2_invalid_stats_range(mock_races_manager, mock_persistence_service):
    """
    Creating a character with stats outside [3, 20] should fail with 400.
    """
    mock_races_manager_instance = mock_races_manager.return_value
    mock_races_manager_instance.get_race_by_id.return_value = MOCK_RACES_DATA[0]

    too_low_stats = {
        "strength": 2,  # invalid (below 3)
        "constitution": 10,
        "agility": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10,
    }
    body = {
        "name": "Bounds Low",
        "race_id": "humans",
        "culture_id": "gondorians",
        "stats": too_low_stats,
        "skills": {"combat": {"Melee Weapons": 1}},
    }
    resp_low = client.post("/api/creation/create", json=body)
    assert resp_low.status_code == 400
    assert "greater than or equal to 3" in resp_low.json()["detail"]

    too_high_stats = {
        "strength": 21,  # invalid (above 20)
        "constitution": 10,
        "agility": 10,
        "intelligence": 10,
        "wisdom": 10,
        "charisma": 10,
    }
    body_high = {
        "name": "Bounds High",
        "race_id": "humans",
        "culture_id": "gondorians",
        "stats": too_high_stats,
        "skills": {"combat": {"Melee Weapons": 1}},
    }
    resp_high = client.post("/api/creation/create", json=body_high)
    assert resp_high.status_code == 400
    assert "less than or equal to 20" in resp_high.json()["detail"]


# --- Tests for /random endpoint ---

MOCK_RANDOM_RACE = RaceData(
    id="elves",
    name="Elves",
    characteristic_bonuses={"Agility": 1},
    base_languages=["Sindarin"],
    optional_languages=[],
    cultures=[
        CultureData(id="rivendell", name="Rivendell Elves", skill_bonuses={"Magic": 1}, traits="Wise and ancient")
    ]
)

MOCK_RANDOM_STATS_INFO = {
    "stats": {
        "strength": {}, "constitution": {}, "agility": {}, 
        "intelligence": {}, "wisdom": {}, "charisma": {}
    }
}

@patch('back.routers.creation.CharacterPersistenceService')
@patch('back.routers.creation.build_simple_gm_agent')
@patch('back.routers.creation.StatsManager')
@patch('back.routers.creation.RacesManager')
@patch('back.routers.creation.random')
def test_create_random_character_success(
    mock_random,
    mock_races_manager,
    mock_stats_manager,
    mock_build_agent,
    mock_persistence_service
):
    """
    Test successful creation of a random character, mocking all external dependencies.
    """
    # --- Mock setup ---
    # Mock RacesManager
    mock_races_manager.return_value.get_all_races.return_value = [MOCK_RANDOM_RACE]
    
    # Mock random.choice to be deterministic
    mock_random.choice.side_effect = [
        MOCK_RANDOM_RACE,  # First call for race
        MOCK_RANDOM_RACE.cultures[0] if MOCK_RANDOM_RACE.cultures else None  # Second call for culture
    ]
    
    # Mock StatsManager
    mock_stats_manager.return_value.get_all_stats_data.return_value = MOCK_RANDOM_STATS_INFO
    
    # Mock random.randint to return a fixed value for stats
    mock_random.randint.return_value = 12
    
    # Mock LLM Agent
    mock_agent = AsyncMock()
    # Mock RunResult objects with .output attribute
    from unittest.mock import MagicMock
    result1 = MagicMock()
    result1.output = "Gandalf"
    result2 = MagicMock()
    result2.output = "A wizard"
    result3 = MagicMock()
    result3.output = "A grey beard"
    mock_agent.run.side_effect = [result1, result2, result3]
    mock_build_agent.return_value = mock_agent
    
    # --- API call ---
    response = client.post("/api/creation/random")
    
    # --- Assertions ---
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "created"
    character = data["character"]
    
    # Assert LLM-generated content
    assert character["name"] == "Gandalf"
    assert character["description"] == "A wizard"
    assert character["physical_description"] == "A grey beard"
    
    # Assert random selections
    assert character["race"] == "elves"
    assert character["culture"] == "rivendell"
    
    # Assert stats
    assert character["stats"]["strength"] == 12
    assert character["stats"]["constitution"] == 12
    
    # Assert calculated combat stats
    # constitution=12 -> max_hp = 12 * 10 + 5 = 125
    # intelligence=12, wisdom=12 -> max_mp = 12 * 5 + 12 * 3 = 96
    assert character["combat_stats"]["max_hit_points"] == 125
    assert character["combat_stats"]["current_hit_points"] == 125
    assert character["combat_stats"]["max_mana_points"] == 96
    assert character["combat_stats"]["current_mana_points"] == 96
    
    # Assert persistence
    mock_persistence_service.save_character_data.assert_called_once()


@patch('back.routers.creation.RacesManager')
def test_create_random_character_no_races(mock_races_manager):
    """
    Test random character creation failure when no races are available.
    """
    mock_races_manager.return_value.get_all_races.return_value = []
    
    response = client.post("/api/creation/random")
    
    assert response.status_code == 500
    assert "No races available" in response.json()["detail"]

@patch('back.routers.creation.RacesManager')
@patch('back.routers.creation.random')
def test_create_random_character_no_cultures(mock_random, mock_races_manager):
    """
    Test random character creation failure when a race has no cultures.
    """
    race_no_culture = RaceData(id="lonely", name="Lonely Race", characteristic_bonuses={}, base_languages=[], optional_languages=[], cultures=[])
    mock_races_manager.return_value.get_all_races.return_value = [race_no_culture]
    mock_random.choice.return_value = race_no_culture
    
    response = client.post("/api/creation/random")
    
    assert response.status_code == 500
    assert "has no cultures" in response.json()["detail"]