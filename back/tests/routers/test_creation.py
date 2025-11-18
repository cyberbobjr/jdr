"""
Tests for character creation router endpoints.

Tests all endpoints in back/routers/creation.py with comprehensive coverage
of success cases, error cases, and edge cases. Mocks external services.
"""

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from uuid import uuid4
from datetime import datetime
from typing import Any, Dict
from back.app import app
from back.models.domain.character import Character, Stats, Skills, CombatStats, Equipment, Spells, CharacterStatus

client = TestClient(app)

# Mock data for races
MOCK_RACES_DATA = [
    MagicMock(id="humans", name="Humans", description="Human race", cultures=[
        MagicMock(id="gondorians", name="Gondorians", description="People of Gondor")
    ])
]

# Mock character data
MOCK_CHARACTER_1 = Character(
    id=uuid4(),
    name="Aragorn",
    race="humans",
    culture="gondorians",
    stats=Stats(strength=15, constitution=14, agility=13, intelligence=12, wisdom=16, charisma=15),
    skills=Skills(combat={"melee_weapons": 3, "weapon_handling": 2}, general={"perception": 4}),
    combat_stats=CombatStats(max_hit_points=140, current_hit_points=140, max_mana_points=112, current_mana_points=112, armor_class=11, attack_bonus=2),
    equipment=Equipment(gold=0),
    spells=Spells(),
    level=1,
    status=CharacterStatus.DRAFT,
    experience_points=0,
    created_at=datetime.now(),
    updated_at=datetime.now(),
    description="Son of Arathorn, heir to the throne of Gondor",
    physical_description="Tall ranger with dark hair and piercing eyes"
)


@patch('back.routers.creation.CharacterPersistenceService')
@patch('back.routers.creation.RacesDataService')
def test_create_character_v2_physical_description_persisted(mock_races_service, mock_persistence_service):
    """
    Test that physical description is properly persisted when creating a character.
    """
    # Setup mocks
    mock_races_service_instance = mock_races_service.return_value
    mock_races_service_instance.get_race_by_id.return_value = MOCK_RACES_DATA[0]

    # Mock persistence service save method
    saved_character = None
    def save_side_effect(cid, data):
        nonlocal saved_character
        saved_character = data
        return data
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

    # Verify that the saved character data contains the physical description
    assert saved_character is not None
    assert saved_character.get("physical_description") == "Scar over left eye"


@patch('back.routers.creation.CharacterPersistenceService')
@patch('back.routers.creation.RacesDataService')
def test_create_character_v2_sets_active_when_complete(mock_races_service, mock_persistence_service):
    """Ensure completed payloads are stored as active characters."""
    mock_races_service_instance = mock_races_service.return_value
    mock_races_service_instance.get_race_by_id.return_value = MOCK_RACES_DATA[0]

    saved_character: Dict[str, Any] | None = None

    def save_side_effect(character_id: str, payload: dict) -> dict:
        nonlocal saved_character
        saved_character = payload
        return payload

    mock_persistence_service.save_character_data.side_effect = save_side_effect

    request_data = {
        "name": "Complete Hero",
        "race_id": "humans",
        "culture_id": "gondorians",
        "stats": {"strength": 14, "constitution": 13, "agility": 12, "intelligence": 11, "wisdom": 10, "charisma": 9},
        "skills": {
            "combat": {"melee_weapons": 10, "weapon_handling": 10},
            "general": {"perception": 10, "crafting": 10}
        },
        "background": "Veteran of countless battles",
        "physical_description": "Tall warrior with a scarred face"
    }

    response = client.post("/api/creation/create", json=request_data)
    assert response.status_code == 200
    assert saved_character is not None
    assert saved_character["status"] == "active"


@patch('back.routers.creation.CharacterPersistenceService')
@patch('back.routers.creation.RacesDataService')
def test_create_character_v2_invalid_race(mock_races_service, mock_persistence_service):
    """
    Test character creation with invalid race.
    """
    # Setup mock to return None for invalid race
    mock_races_service_instance = mock_races_service.return_value
    mock_races_service_instance.get_race_by_id.return_value = None

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
    """
    Test successful character update.
    """
    character_id = str(uuid4())
    existing_character = MOCK_CHARACTER_1.model_copy()
    # Skip assignment for test purposes - existing character already has an id
    existing_character.name = "Old Name"

    # Mock persistence service
    mock_persistence_service.load_character_data.return_value = existing_character

    request_data = {
        "character_id": character_id,
        "name": "Updated Name",
        "physical_description": "Updated description"
    }

    response = client.post("/api/creation/update", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "updated"
    assert data["character"]["name"] == "Updated Name"
    assert data["character"]["physical_description"] == "Updated description"

    # Verify the service methods were called
    mock_persistence_service.load_character_data.assert_called_once_with(character_id)
    mock_persistence_service.save_character_data.assert_called_once()


@patch('back.routers.creation.CharacterPersistenceService')
def test_update_character_v2_sets_active_when_complete(mock_persistence_service):
    """Ensure updates flip status to active once every section is filled."""
    character_id = str(uuid4())
    existing_character = MOCK_CHARACTER_1.model_copy()
    existing_character.stats = Stats(strength=15, constitution=14, agility=13, intelligence=12, wisdom=11, charisma=10)
    existing_character.skills = Skills(
        combat={"melee_weapons": 10, "weapon_handling": 10},
        general={"perception": 10, "crafting": 10}
    )
    existing_character.description = None
    existing_character.physical_description = None
    existing_character.status = CharacterStatus.DRAFT

    mock_persistence_service.load_character_data.return_value = existing_character

    saved_character: Character | None = None

    def save_side_effect(character_id: str, payload: Character) -> Character:
        nonlocal saved_character
        saved_character = payload
        return payload

    mock_persistence_service.save_character_data.side_effect = save_side_effect

    request_data = {
        "character_id": character_id,
        "background": "Strategist of the White City",
        "physical_description": "Graceful yet imposing presence"
    }

    response = client.post("/api/creation/update", json=request_data)
    assert response.status_code == 200
    assert saved_character is not None
    assert saved_character.status == CharacterStatus.ACTIVE


@patch('back.routers.creation.CharacterPersistenceService')
def test_update_character_v2_not_found(mock_persistence_service):
    """
    Test updating non-existent character.
    """
    character_id = str(uuid4())
    # Mock persistence service to return None (character not found)
    mock_persistence_service.load_character_data.return_value = None

    request_data = {
        "character_id": character_id,
        "name": "Updated Name"
    }

    response = client.post("/api/creation/update", json=request_data)
    assert response.status_code == 404
    assert f"Character with id '{character_id}' not found" in response.json()["detail"]

    # Ensure save was not called
    mock_persistence_service.save_character_data.assert_not_called()




@patch('back.routers.creation.CharacterPersistenceService')
def test_create_character_v2_missing_stats(mock_persistence_service):
    """
    Ensure default stats are applied when not provided in the request.
    """
    mock_races_service_instance = MagicMock()
    mock_races_service_instance.get_race_by_id.return_value = MOCK_RACES_DATA[0]

    with patch('back.routers.creation.RacesDataService', return_value=mock_races_service_instance):
        saved_payload: Dict[str, Any] = {}

        def save_side_effect(character_id: str, character_data: dict) -> dict:
            saved_payload["character_id"] = character_id
            saved_payload["data"] = character_data
            return character_data

        mock_persistence_service.save_character_data.side_effect = save_side_effect

        request_data = {
            "name": "Test Character",
            "race_id": "humans",
            "culture_id": "gondorians",
            # Missing stats - the router should fall back to default values
            "skills": {"combat": {"Melee Weapons": 1}}
        }

        response = client.post("/api/creation/create", json=request_data)
        assert response.status_code == 200
        response_data = response.json()
        assert "character_id" in response_data

        assert "data" in saved_payload
        stats = saved_payload["data"]["stats"]
        assert all(value == 10 for value in stats.values())


@patch('back.routers.creation.CharacterPersistenceService')
@patch('back.routers.creation.RacesDataService')
def test_create_character_v2_service_error(mock_races_service, mock_persistence_service):
    """
    Test character creation when service raises an exception.
    """
    # Setup mocks
    mock_races_service_instance = mock_races_service.return_value
    mock_races_service_instance.get_race_by_id.return_value = MOCK_RACES_DATA[0]

    # Mock persistence service to raise an exception
    mock_persistence_service.save_character_data.side_effect = Exception("Database error")

    request_data = {
        "name": "Test Character",
        "race_id": "humans",
        "culture_id": "gondorians",
        "stats": {"strength": 10, "constitution": 10, "agility": 10, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "skills": {"combat": {"Melee Weapons": 1}}
    }

    response = client.post("/api/creation/create", json=request_data)
    assert response.status_code == 500
    assert "Character creation failed" in response.json()["detail"]


@patch('back.routers.creation.CharacterPersistenceService')
def test_validate_character_v2_success(mock_persistence_service):
    """
    Test successful character validation.
    """
    character_data = {
        "id": str(uuid4()),
        "name": "Test Character",
        "race": "humans",
        "culture": "gondorians",
        "stats": {"strength": 15, "constitution": 14, "agility": 13, "intelligence": 12, "wisdom": 16, "charisma": 15},
        "skills": {"combat": {"melee_weapons": 3}},
        "combat_stats": {"max_hit_points": 140, "current_hit_points": 140, "max_mana_points": 112, "current_mana_points": 112, "armor_class": 11, "attack_bonus": 2},
        "equipment": {"weapons": [], "armor": [], "accessories": [], "consumables": [], "gold": 0},
        "spells": {"known_spells": [], "spell_slots": {}, "spell_bonus": 0},
        "level": 1,
        "status": "draft",
        "experience_points": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "description": "Test character",
        "physical_description": "Test description"
    }

    response = client.post("/api/creation/validate-character", json=character_data)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    assert "message" in data


@patch('back.routers.creation.CharacterPersistenceService')
def test_validate_character_v2_invalid_data(mock_persistence_service):
    """
    Test character validation with invalid data.
    """
    invalid_character_data = {
        "id": str(uuid4()),
        "name": "",  # Invalid: empty name
        "race": "humans",
        "culture": "gondorians",
        "stats": {"strength": 15, "constitution": 14, "agility": 13, "intelligence": 12, "wisdom": 16, "charisma": 15},
        "skills": {"combat": {"melee_weapons": 3}},
        "combat_stats": {"max_hit_points": 140, "current_hit_points": 140, "max_mana_points": 112, "current_mana_points": 112, "armor_class": 11, "attack_bonus": 2},
        "equipment": {"weapons": [], "armor": [], "accessories": [], "consumables": [], "gold": 0},
        "spells": {"known_spells": [], "spell_slots": {}, "spell_bonus": 0},
        "level": 1,
        "status": "draft",
        "experience_points": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "description": "Test character",
        "physical_description": "Test description"
    }

    response = client.post("/api/creation/validate-character", json=invalid_character_data)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == False
    assert len(data["errors"]) > 0


@patch('back.routers.creation.CharacterPersistenceService')
def test_validate_character_by_id_success(mock_persistence_service):
    """Validate a stored character using only its identifier."""
    stored_character = MOCK_CHARACTER_1.model_copy()
    mock_persistence_service.load_character_data.return_value = stored_character

    response = client.post(
        "/api/creation/validate-character/by-id",
        json={"character_id": str(stored_character.id)},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is True
    mock_persistence_service.load_character_data.assert_called_once_with(str(stored_character.id))


@patch('back.routers.creation.CharacterPersistenceService')
def test_validate_character_by_id_not_found(mock_persistence_service):
    """Return 404 when the character JSON file cannot be located."""
    mock_persistence_service.load_character_data.side_effect = FileNotFoundError("missing")

    response = client.post(
        "/api/creation/validate-character/by-id",
        json={"character_id": str(uuid4())},
    )

    assert response.status_code == 404
    assert "missing" in response.json()["detail"]


@patch('back.routers.creation.CharacterPersistenceService')
def test_validate_character_by_id_invalid_payload(mock_persistence_service):
    """Surface validation errors when the stored payload is incomplete."""
    invalid_character = MagicMock()
    invalid_character.model_dump.return_value = {
        "id": str(uuid4()),
        "name": "",
        "race": "humans",
        "culture": "gondorians",
        "stats": {},
        "skills": {},
        "combat_stats": {},
        "equipment": {},
        "spells": {},
        "level": 1,
        "status": "draft",
        "experience_points": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "description": None,
        "physical_description": None,
    }

    mock_persistence_service.load_character_data.return_value = invalid_character

    response = client.post(
        "/api/creation/validate-character/by-id",
        json={"character_id": str(uuid4())},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["valid"] is False
    assert payload["errors"]