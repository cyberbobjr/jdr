
# Ajouter les imports nécessaires pour les tests FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
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
    "skills_for_llm": [
        {"name": "Melee Weapons", "description": "Proficiency with close-quarters weapons like swords, axes, and spears."},
    ],
    "skill_groups": {
        "Combat": [
            {"name": "Melee Weapons", "description": "Proficiency with close-quarters weapons like swords, axes, and spears."}
        ]
    }
}

MOCK_EQUIPMENT_DATA = {
    "weapons": {
        "Longsword": {
            "type": "weapon",
            "category": "melee",
            "damage": "1d8+4",
            "weight": 1.5,
            "cost": 2,
            "description": "Balanced and versatile one-handed sword"
        }
    }
}

MOCK_STATS_DATA = {
    "stats": {
        "Strength": {
            "short_name": "STR",
            "category": "physical",
            "description": "Physical strength, build. Determines melee damage and carrying capacity.",
            "examples": ["Lifting heavy objects"]
        }
    }
}

@patch('back.routers.creation.RacesManager')
def test_get_races(mock_races_manager):
    mock_races_manager_instance = mock_races_manager.return_value
    mock_races_manager_instance.get_all_races.return_value = MOCK_RACES_DATA
    
    response = client.get("/api/creation/races")
    assert response.status_code == 200
    assert response.json() == [race.model_dump() for race in MOCK_RACES_DATA]

@patch('back.routers.creation.SkillsManager')
def test_get_skills(mock_skills_manager):
    mock_skills_manager_instance = mock_skills_manager.return_value
    mock_skills_manager_instance.skills_data = MOCK_SKILLS_DATA["skills_for_llm"]
    mock_skills_manager_instance.skill_groups = MOCK_SKILLS_DATA["skill_groups"]
    
    response = client.get("/api/creation/skills")
    assert response.status_code == 200
    assert response.json() == MOCK_SKILLS_DATA

@patch('back.routers.creation.EquipmentManager')
def test_get_equipment(mock_equipment_manager):
    mock_equipment_manager_instance = mock_equipment_manager.return_value
    mock_equipment_manager_instance.get_all_equipment.return_value = MOCK_EQUIPMENT_DATA
    
    response = client.get("/api/creation/equipment")
    assert response.status_code == 200
    assert response.json() == MOCK_EQUIPMENT_DATA

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
        "skills": {"combat": {"Melee Weapons": 1}}
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
        "background": "Updated background"
    }
    
    response = client.post("/api/creation/update", json=update_data)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "updated"
    assert response_data["character"]["name"] == "New Name"
    assert response_data["character"]["stats"]["strength"] == 12
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
    assert response.status_code == 200 # FastAPI returns 200 for validation errors in this endpoint
    response_data = response.json()
    assert response_data["valid"] is False
    assert "Validation failed:" in response_data["message"]
    assert "errors" in response_data