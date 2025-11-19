"""
FastAPI router for character creation V2.
Exposes the necessary routes for the new simplified character system using CharacterV2 models.
"""

from fastapi import APIRouter, HTTPException
from uuid import uuid4
from datetime import datetime
from typing import List, Dict, Any

from back.models.domain.character import Character, Stats, Skills
from back.services.character_data_service import CharacterDataService
from back.services.skill_allocation_service import SkillAllocationService
from back.services.races_data_service import RacesDataService
from back.models.domain.stats_manager import StatsManager
from back.models.domain.equipment_manager import EquipmentManager
from back.models.domain.unified_skills_manager import UnifiedSkillsManager
from back.models.schema import RaceData, SkillsResponse, EquipmentResponse, StatsResponse, EquipmentItem
from back.agents.gm_agent_pydantic import build_simple_gm_agent
import random

router = APIRouter(tags=["creation"])

# Pydantic models for requests/responses
from pydantic import BaseModel, Field

class CreateCharacterV2Request(BaseModel):
    """Request model for creating a new V2 character"""
    name: str = Field(..., description="Character name")
    race_id: str = Field(..., description="Race ID")
    culture_id: str = Field(..., description="Culture ID")
    stats: Dict[str, int] = Field(default={}, description="Character stats")
    skills: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Character skills by group")
    background: str = Field(default="", description="Character background")
    physical_description: str | None = Field(default=None, description="Physical appearance description")

class CreateCharacterV2Response(BaseModel):
    """Response model for character creation"""
    character_id: str = Field(..., description="Unique character identifier")
    status: str = Field(..., description="Creation status")
    created_at: str = Field(..., description="Creation timestamp")

class UpdateCharacterV2Request(BaseModel):
    """Request model for updating a V2 character"""
    character_id: str = Field(..., description="Character ID")
    name: str = Field(default="", description="Character name")
    stats: Dict[str, int] = Field(default_factory=dict, description="Character stats")
    skills: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Character skills by group")
    background: str = Field(default="", description="Character background")
    physical_description: str | None = Field(default=None, description="Physical appearance description")

class UpdateCharacterV2Response(BaseModel):
    """Response model for character update"""
    character: Dict[str, Any] = Field(..., description="Updated character data")
    status: str = Field(..., description="Update status")

class CharacterV2Response(BaseModel):
    """Response model for character data"""
    character: Character = Field(..., description="Character data")
    status: str = Field(..., description="Operation status")

class ValidateCharacterV2Request(BaseModel):
    """Request model for character validation"""
    id: str = Field(..., description="Character ID")
    name: str = Field(..., description="Character name")
    race: str = Field(..., description="Race ID")
    culture: str = Field(..., description="Culture ID")
    stats: Dict[str, int] = Field(..., description="Character stats")
    skills: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Character skills by group")
    combat_stats: Dict[str, Any] = Field(..., description="Combat statistics")
    equipment: Dict[str, Any] = Field(..., description="Equipment data")
    spells: Dict[str, Any] = Field(..., description="Spell data")
    level: int = Field(..., description="Character level")
    status: str = Field(..., description="Character status")
    experience_points: int = Field(..., description="Experience points")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    description: str | None = Field(default=None, description="Character description")
    physical_description: str | None = Field(default=None, description="Physical description")

class ValidateCharacterV2Response(BaseModel):
    """Response model for character validation"""
    valid: bool = Field(..., description="Whether the character is valid")
    character: Dict[str, Any] = Field(default_factory=dict, description="Validated character data (if valid)")
    errors: List[str] = Field(default_factory=list, description="Validation errors (if invalid)")
    message: str = Field(..., description="Validation message")


def _validate_character_payload(character_payload: Dict[str, Any], character_id: str | None = None) -> ValidateCharacterV2Response:
    """Run CharacterV2 validation and build a standardized response.
    
    If character_id is provided, persists any status changes after validation.
    """
    try:
        validated_character = Character(**character_payload)
        validated_character.sync_status_from_completion()
        
        # Persist status change if character_id is provided
        if character_id:
            CharacterDataService().save_character(validated_character, character_id)
        
        return ValidateCharacterV2Response(
            valid=True,
            character=validated_character.model_dump(),
            message="Character is valid",
        )
    except ValueError as validation_error:
        return ValidateCharacterV2Response(
            valid=False,
            errors=[str(validation_error)],
            message=f"Validation failed: {str(validation_error)}",
        )


class ValidateCharacterByIdRequest(BaseModel):
    """Request model for validating a character stored on disk."""
    character_id: str = Field(..., description="Identifier of the character to validate")

@router.post(
    "/random",
    response_model=CharacterV2Response,
    summary="Create a random V2 character",
    description="Creates a new random character using the simplified V2 system, including LLM-generated name, background and description."
)
async def create_random_character() -> CharacterV2Response:
    """
    Creates a new random character using the V2 system with LLM-generated content.

    **Response:**
    ```json
    {
        "character": {
            "id": "d7763165-4c03-4c8d-9bc6-6a2568b79eb3",
            "name": "Eldarion",
            "race": "elves",
            "culture": "rivendell",
            "stats": {
                "strength": 12,
                "constitution": 13,
                "agility": 15,
                "intelligence": 14,
                "wisdom": 11,
                "charisma": 16
            },
            "skills": {
                "combat": {
                    "melee_weapons": 5,
                    "weapon_handling": 3
                },
                "general": {
                    "perception": 4,
                    "herbalism": 2
                }
            },
            "combat_stats": {
                "max_hit_points": 135,
                "current_hit_points": 135,
                "max_mana_points": 104,
                "current_mana_points": 104,
                "armor_class": 12,
                "attack_bonus": 1
            },
            "equipment": {
                "weapons": [],
                "armor": [],
                "accessories": [],
                "consumables": [],
                "gold": 0
            },
            "spells": {
                "known_spells": [],
                "spell_slots": {},
                "spell_bonus": 0
            },
            "level": 1,
            "status": "draft",
            "experience_points": 0,
            "created_at": "2025-11-13T21:30:00Z",
            "updated_at": "2025-11-13T21:30:00Z",
            "description": "A wise elf from the ancient forests",
            "physical_description": "Tall with silver hair and piercing blue eyes"
        },
        "status": "created"
    }
    ```
    """
    try:
        # 1. Get random race and culture
        races_service = RacesDataService()
        try:
            random_race_data, random_culture_data = races_service.get_random_race_and_culture()
        except ValueError as error:
            raise HTTPException(status_code=500, detail=str(error))

        # 2. Generate random stats
        stats_manager = StatsManager()
        stats_info = stats_manager.get_all_stats_data()['stats']
        random_stats = {stat.lower(): random.randint(8, 15) for stat in stats_info}

        # 3. Allocate skills based on race affinities and stats
        skill_allocation_service = SkillAllocationService()
        stats_obj = Stats(**random_stats)
        allocated_skills = skill_allocation_service.allocate_random_skills_for_character(
            random_race_data.name, random_culture_data.name, stats_obj
        )

        # 4. Generate name, background and description with LLM
        agent = build_simple_gm_agent()

        name_prompt = f"Generate a single fantasy name for a {random_race_data.name} from {random_culture_data.name}. Only return the name."
        background_prompt = f"Generate a short background story for a {random_race_data.name} from {random_culture_data.name}. Be creative and concise."
        description_prompt = f"Generate a short physical description for a {random_race_data.name} from {random_culture_data.name}. Be creative and concise."

        character_name = (await agent.run(name_prompt)).output
        background = (await agent.run(background_prompt)).output
        physical_description = (await agent.run(description_prompt)).output

        # 4. Calculate combat stats
        strength_modifier = (random_stats['strength'] - 10) // 2
        agility_modifier = (random_stats['agility'] - 10) // 2
        
        max_hp = random_stats['constitution'] * 10 + 5 # level 1
        max_mp = random_stats['intelligence'] * 5 + random_stats['wisdom'] * 3
        ac = 10 + agility_modifier
        attack_bonus = strength_modifier

        # 5. Create and save character
        character_id = str(uuid4())
        now = datetime.now().isoformat()

        character_dict = {
            "id": character_id,
            "name": character_name,
            "race": random_race_data.id,
            "culture": random_culture_data.id,
            "stats": Stats(**random_stats).model_dump(),
            "skills": allocated_skills,
            "combat_stats": {
                "max_hit_points": max_hp, "current_hit_points": max_hp, 
                "max_mana_points": max_mp, "current_mana_points": max_mp, 
                "armor_class": ac, "attack_bonus": attack_bonus
            },
            "equipment": {"weapons": [], "armor": [], "accessories": [], "consumables": [], "gold": 0},
            "spells": {"known_spells": [], "spell_slots": {}, "spell_bonus": 0},
            "level": 1, "status": "draft", "experience_points": 0,
            "created_at": now, "updated_at": now,
            "description": background,
            "physical_description": physical_description
        }
        
        character = Character(**character_dict)
        character.sync_status_from_completion()
        CharacterDataService().save_character(character, character_id)
        
        return CharacterV2Response(
            character=character,
            status="created"
        )

    except Exception as e:
        # Log the full error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Random character creation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Random character creation failed: {str(e)}")

@router.get("/races", summary="List of races V2", response_model=List[RaceData])
def get_races() -> List[RaceData]:
    """
    Returns the complete list of available races for the V2 system.

    **Response:**
    ```json
    [
        {
            "id": "elves",
            "name": "Elves",
            "description": "Graceful and long-lived beings with affinity for magic and nature",
            "cultures": [
                {
                    "id": "noldor",
                    "name": "Noldor",
                    "description": "The wise and skilled craftsmen of the Elves"
                }
            ],
            "stat_bonuses": {
                "intelligence": 2,
                "wisdom": 1
            }
        }
    ]
    ```
    """
    races_service = RacesDataService()
    races_data = races_service.get_all_races()

    # FastAPI will automatically serialize RaceData Pydantic objects to JSON
    return races_data

@router.get("/skills", summary="Skills data V2", response_model=SkillsResponse)
def get_skills() -> SkillsResponse:
    """
    Returns the complete skills structure for the V2 system including racial affinities.

    **Response:**
    ```json
    {
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
          {"skill": "crafting", "base_points": 3},
          {"skill": "general_knowledge", "base_points": 3}
        ]
      }
    }
    ```
    """
    skills_manager = UnifiedSkillsManager()
    data = skills_manager.get_all_data()
    return SkillsResponse(**data)

@router.get("/equipment", summary="Equipment data V2", response_model=EquipmentResponse)
def get_equipment() -> EquipmentResponse:
    """
    Returns the complete equipment structure for the V2 system.

    **Response:**
    ```json
    {
        "weapons": [
            {
                "id": "longsword",
                "name": "Longsword",
                "category": "weapon",
                "cost": 15.0,
                "weight": 3.0,
                "quantity": 1,
                "equipped": false,
                "description": "A well-balanced one-handed sword",
                "damage": "1d8"
            }
        ],
        "armor": [
            {
                "id": "chain_mail",
                "name": "Chain Mail",
                "category": "armor",
                "cost": 75.0,
                "weight": 55.0,
                "quantity": 1,
                "equipped": false,
                "description": "Flexible metal armor",
                "protection": 16
            }
        ],
        "accessories": [],
        "consumables": []
    }
    ```
    """
    equipment_manager = EquipmentManager()
    equipment_data = equipment_manager.get_all_equipment()

    # Convert dictionaries to EquipmentItem objects, handling type conversions
    def convert_item(item: dict) -> EquipmentItem:
        # Convert range to string if it's an integer
        if 'range' in item and isinstance(item['range'], int):
            item['range'] = str(item['range'])
        return EquipmentItem(**item)

    weapons = [convert_item(item) for item in equipment_data.get("weapons", [])]
    armor = [convert_item(item) for item in equipment_data.get("armor", [])]
    accessories = [convert_item(item) for item in equipment_data.get("accessories", [])]
    consumables = [convert_item(item) for item in equipment_data.get("consumables", [])]

    return EquipmentResponse(
        weapons=weapons,
        armor=armor,
        accessories=accessories,
        consumables=consumables
    )

@router.get("/stats", summary="Stats data V2", response_model=StatsResponse)
def get_stats() -> StatsResponse:
    """
    Returns the complete stats structure for the V2 system.

    **Response:**
    ```json
    {
        "stats": {
            "strength": {
                "id": "strength",
                "name": "Strength",
                "description": "Physical power and muscle",
                "min_value": 3,
                "max_value": 20
            },
            "constitution": {
                "id": "constitution",
                "name": "Constitution",
                "description": "Physical health and endurance",
                "min_value": 3,
                "max_value": 20
            }
        },
        "value_range": {
            "min": 3,
            "max": 20
        },
        "bonus_formula": "(value - 10) // 2",
        "bonus_table": {},
        "cost_table": {},
        "starting_points": null
    }
    ```
    """
    stats_manager = StatsManager()
    stats_data = stats_manager.get_all_stats_data()

    # StatsManager returns data that matches StatsResponse structure
    return StatsResponse(**stats_data)

@router.post(
    "/create",
    response_model=CreateCharacterV2Response,
    summary="Create a new V2 character",
    description="Creates a new character using the simplified V2 system"
)
def create_character(request: CreateCharacterV2Request) -> CreateCharacterV2Response:
    """
    Creates a new character using the V2 system with validation.

    **Request Body:**
    ```json
    {
        "name": "Aragorn",
        "race_id": "humans",
        "culture_id": "gondorians",
        "stats": {
            "strength": 15,
            "constitution": 14,
            "agility": 13,
            "intelligence": 12,
            "wisdom": 16,
            "charisma": 15
        },
        "skills": {
            "combat": {
                "melee_weapons": 3,
                "weapon_handling": 2
            },
            "general": {
                "perception": 4
            }
        },
        "background": "Son of Arathorn, heir to the throne of Gondor",
        "physical_description": "Tall ranger with dark hair and piercing eyes"
    }
    ```

    **Response:**
    ```json
    {
        "character_id": "d7763165-4c03-4c8d-9bc6-6a2568b79eb3",
        "status": "created",
        "created_at": "2025-11-13T21:30:00Z"
    }
    ```
    """
    # Define custom exception for race validation
    class RaceNotFoundError(ValueError):
        pass

    try:
        # Generate unique character ID
        character_id = str(uuid4())
        now = datetime.now().isoformat()
        
        # Validate race and culture
        races_service = RacesDataService()
        race_data = races_service.get_race_by_id(request.race_id)
        if not race_data:
            raise RaceNotFoundError(f"Race with id '{request.race_id}' not found")
        
        # Create character using V2 model
        # Create character dictionary directly for V2 model
        
        # Calculate combat stats
        stats_data = request.stats if request.stats else {'strength': 10, 'constitution': 10, 'agility': 10, 'intelligence': 10, 'wisdom': 10, 'charisma': 10}
        
        strength_modifier = (stats_data['strength'] - 10) // 2
        agility_modifier = (stats_data['agility'] - 10) // 2
        
        max_hp = stats_data['constitution'] * 10 + 5 # level 1
        max_mp = stats_data['intelligence'] * 5 + stats_data['wisdom'] * 3
        ac = 10 + agility_modifier
        attack_bonus = strength_modifier

        character_dict = {
            "id": character_id,
            "name": request.name,
            "race": request.race_id,
            "culture": request.culture_id,
            "stats": Stats(**stats_data).model_dump(),
            "skills": Skills(**request.skills).model_dump() if request.skills else Skills().model_dump(),
            "combat_stats": {
                "max_hit_points": max_hp,
                "current_hit_points": max_hp,
                "max_mana_points": max_mp,
                "current_mana_points": max_mp,
                "armor_class": ac,
                "attack_bonus": attack_bonus
            },
            "equipment": {
                "weapons": [],
                "armor": [],
                "accessories": [],
                "consumables": [],
                "gold": 0
            },
            "spells": {
                "known_spells": [],
                "spell_slots": {},
                "spell_bonus": 0
            },
            "level": 1,
            "status": "draft",
            "experience_points": 0,
            "created_at": now,
            "updated_at": now,
            "description": request.background or None,
            "physical_description": request.physical_description
        }
        
        # Validate using Character model and align status with completion state
        character = Character(**character_dict)
        character.sync_status_from_completion()

        # Save character data
        CharacterDataService().save_character(character, character_id)
        
        return CreateCharacterV2Response(
            character_id=character_id,
            status="created",
            created_at=now
        )
        
    except RaceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Character creation failed: {str(e)}")

@router.post(
    "/update",
    response_model=UpdateCharacterV2Response,
    summary="Update V2 character",
    description="Updates an existing V2 character"
)
def update_character(request: UpdateCharacterV2Request) -> UpdateCharacterV2Response:
    """
    Updates an existing V2 character with validation.

    **Request Body:**
    ```json
    {
        "character_id": "d7763165-4c03-4c8d-9bc6-6a2568b79eb3",
        "name": "Aragorn II",
        "stats": {
            "strength": 16,
            "constitution": 15,
            "agility": 14,
            "intelligence": 13,
            "wisdom": 17,
            "charisma": 16
        },
        "skills": {
            "combat": {
                "melee_weapons": 5,
                "weapon_handling": 4
            }
        },
        "background": "Heir to the throne of Gondor, skilled ranger",
        "physical_description": "Tall with dark hair and noble bearing"
    }
    ```

    **Response:**
    ```json
    {
        "character": {
            "id": "d7763165-4c03-4c8d-9bc6-6a2568b79eb3",
            "name": "Aragorn II",
            "race": "humans",
            "culture": "gondorians",
            "stats": {
                "strength": 16,
                "constitution": 15,
                "agility": 14,
                "intelligence": 13,
                "wisdom": 17,
                "charisma": 16
            },
            "skills": {
                "combat": {
                    "melee_weapons": 5,
                    "weapon_handling": 4
                }
            },
            "combat_stats": {
                "max_hit_points": 150,
                "current_hit_points": 150,
                "max_mana_points": 130,
                "current_mana_points": 130,
                "armor_class": 12,
                "attack_bonus": 3
            },
            "equipment": {
                "weapons": [],
                "armor": [],
                "accessories": [],
                "consumables": [],
                "gold": 0
            },
            "spells": {
                "known_spells": [],
                "spell_slots": {},
                "spell_bonus": 0
            },
            "level": 1,
            "status": "draft",
            "experience_points": 0,
            "created_at": "2025-11-13T21:30:00Z",
            "updated_at": "2025-11-13T21:35:00Z",
            "description": "Heir to the throne of Gondor, skilled ranger",
            "physical_description": "Tall with dark hair and noble bearing"
        },
        "status": "updated"
    }
    ```
    """
    # Define custom exception for character not found
    class CharacterNotFoundError(ValueError):
        pass
    
    try:
        # Load existing character
        existing_character = CharacterDataService().load_character(request.character_id)
        if existing_character is None:
            raise CharacterNotFoundError(f"Character with id '{request.character_id}' not found")

        # Update fields
        if request.name:
            existing_character.name = request.name
        if request.stats:
            existing_character.stats = Stats(**request.stats)
        if request.skills:
            existing_character.skills = Skills(**request.skills)
        if request.background:
            existing_character.description = request.background
        if request.physical_description is not None:
            existing_character.physical_description = request.physical_description

        existing_character.sync_status_from_completion()
        existing_character.update_timestamp()

        # 3. Save updated character
        CharacterDataService().save_character(existing_character, request.character_id)
        
        return UpdateCharacterV2Response(
            character=existing_character.model_dump(),
            status="updated"
        )
        
    except CharacterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Character update failed: {str(e)}")



@router.post(
    "/validate-character",
    response_model=ValidateCharacterV2Response,
    summary="Validate character",
    description="Validates a character against game rules"
)
async def validate_character(character: ValidateCharacterV2Request) -> ValidateCharacterV2Response:
    """
    Validates a character against game rules.

    **Request Body:**
    ```json
    {
        "id": "d7763165-4c03-4c8d-9bc6-6a2568b79eb3",
        "name": "Aragorn",
        "race": "humans",
        "culture": "gondorians",
        "stats": {
            "strength": 15,
            "constitution": 14,
            "agility": 13,
            "intelligence": 12,
            "wisdom": 16,
            "charisma": 15
        },
        "skills": {
            "combat": {
                "melee_weapons": 3
            }
        },
        "combat_stats": {
            "max_hit_points": 140,
            "current_hit_points": 140,
            "max_mana_points": 112,
            "current_mana_points": 112,
            "armor_class": 11,
            "attack_bonus": 2
        },
        "equipment": {
            "weapons": [],
            "armor": [],
            "accessories": [],
            "consumables": [],
            "gold": 0
        },
        "spells": {
            "known_spells": [],
            "spell_slots": {},
            "spell_bonus": 0
        },
        "level": 1,
        "status": "draft",
        "experience_points": 0,
        "created_at": "2025-11-13T21:30:00Z",
        "updated_at": "2025-11-13T21:30:00Z",
        "description": "Son of Arathorn",
        "physical_description": "Tall ranger"
    }
    ```

    **Response (Success):**
    ```json
    {
        "valid": true,
        "character": {
            "id": "d7763165-4c03-4c8d-9bc6-6a2568b79eb3",
            "name": "Aragorn",
            "race": "humans",
            "culture": "gondorians",
            "stats": {
                "strength": 15,
                "constitution": 14,
                "agility": 13,
                "intelligence": 12,
                "wisdom": 16,
                "charisma": 15
            },
            "skills": {
                "combat": {
                    "melee_weapons": 3
                }
            },
            "combat_stats": {
                "max_hit_points": 140,
                "current_hit_points": 140,
                "max_mana_points": 112,
                "current_mana_points": 112,
                "armor_class": 11,
                "attack_bonus": 2
            },
            "equipment": {
                "weapons": [],
                "armor": [],
                "accessories": [],
                "consumables": [],
                "gold": 0
            },
            "spells": {
                "known_spells": [],
                "spell_slots": {},
                "spell_bonus": 0
            },
            "level": 1,
            "status": "draft",
            "experience_points": 0,
            "created_at": "2025-11-13T21:30:00Z",
            "updated_at": "2025-11-13T21:30:00Z",
            "description": "Son of Arathorn",
            "physical_description": "Tall ranger"
        },
        "message": "Character is valid"
    }
    ```

    **Response (Failure):**
    ```json
    {
        "valid": false,
        "errors": ["Field 'name' is required"],
        "message": "Validation failed: Field 'name' is required"
    }
    ```
    """
    try:
        return _validate_character_payload(character.model_dump())
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(exc)}") from exc


@router.post(
    "/validate-character/by-id",
    response_model=ValidateCharacterV2Response,
    summary="Validate character by identifier",
    description="Loads a stored character by ID and validates it using the same rules as /validate-character",
)
async def validate_character_by_id(request: ValidateCharacterByIdRequest) -> ValidateCharacterV2Response:
    """Validate a persisted character without resending its entire payload."""
    try:
        character = CharacterDataService().load_character(request.character_id)
    except FileNotFoundError as not_found_error:
        raise HTTPException(status_code=404, detail=str(not_found_error)) from not_found_error
    except ValueError as value_error:
        raise HTTPException(status_code=400, detail=str(value_error)) from value_error

    return _validate_character_payload(character.model_dump(), character_id=request.character_id)