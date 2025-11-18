from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import BaseModel

from back.models.domain.character import Character
from back.services.character_data_service import CharacterDataService
from back.services.character_persistence_service import CharacterPersistenceService
from back.utils.exceptions import InternalServerError
from back.utils.logger import log_debug

class CharacterV2Response(BaseModel):
    """Response model for character data"""
    character: Character
    status: str

router = APIRouter(tags=["characters"])


@router.get("/", response_model=List[Character])
async def list_characters():
    """
    Retrieve the list of all available characters in the system.

    This endpoint allows obtaining all created characters, whether complete or in progress.
    Incomplete characters (status="draft") are returned with only the available fields.

    Returns:
        CharacterListResponse: A list containing all available characters (complete or partial)

    Example Response:

    ```json
        {
            "characters": [
                {
                    "id": "d7763165-4c03-4c8d-9bc6-6a2568b79eb3",
                    "name": "Aragorn",
                    "race": "Human",
                    "culture": "Gondor",
                    "stats": {
                        "strength": 16,
                        "constitution": 14,
                        "agility": 15,
                        "intelligence": 12,
                        "wisdom": 14,
                        "charisma": 16
                    },
                    "skills": {
                        "combat": {"sword_combat": 7, "archery": 5}
                    },
                    "combat_stats": {
                        "max_hit_points": 60,
                        "current_hit_points": 60,
                        "max_mana_points": 15,
                        "current_mana_points": 15,
                        "armor_class": 17,
                        "attack_bonus": 5
                    },
                    "equipment": {
                        "gold": 100
                    },
                    "spells": {
                        "known_spells": [],
                        "spell_slots": {}
                    },
                    "level": 5,
                    "status": "active",
                    "experience_points": 4500,
                    "physical_description": "Tall, weathered, dark-haired, with keen grey eyes."
                }
            ]
        }
        ```

    Raises:
        500: Internal server error when retrieving characters
    """
    log_debug("Appel endpoint characters/list_characters")
    
    try:
        data_service = CharacterDataService()
        characters = data_service.get_all_characters()
        
        log_debug("Liste des personnages récupérée",
                  action="list_characters_success",
                  count=len(characters))

        return characters
        
    except Exception as e:
        log_debug("Erreur lors de la récupération des personnages", 
                 action="list_characters_error", 
                 error=str(e))
        raise InternalServerError(f"Erreur lors de la récupération des personnages: {str(e)}")


@router.get(
    "/{character_id}",
    response_model=CharacterV2Response,
    summary="Get character",
    description="Retrieves a character by ID"
)
async def get_character_detail(character_id: str) -> CharacterV2Response:
    """
    Retrieves a character by ID.

    **Parameters:**
    - `character_id`: UUID string of the character to retrieve

    **Response:**
    ```json
    {
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
                    "melee_weapons": 3,
                    "weapon_handling": 2
                },
                "general": {
                    "perception": 4
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
            "description": "Son of Arathorn, heir to the throne of Gondor",
            "physical_description": "Tall and swift"
        },
        "status": "loaded"
    }
    ```
    """
    try:
        character = CharacterPersistenceService.load_character_data(character_id)
        if character is None:
            raise HTTPException(status_code=404, detail=f"Character with id '{character_id}' not found")

        return CharacterV2Response(
            character=character,
            status="loaded"
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException as e:
        # Re-raise HTTP exceptions without altering the status code
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Character retrieval failed: {str(e)}")


@router.delete(
    "/character/{character_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete V2 character",
    description="Deletes a V2 character by ID"
)
async def delete_character_v2(character_id: str) -> None:
    """
    Deletes a V2 character by ID.
    - **Input**: character_id
    - **Output**: 204 No Content if successful
    """
    try:
        data = CharacterPersistenceService.load_character_data(character_id)  # Verify character exists
        if not data:
            raise HTTPException(status_code=404, detail=f"Character with id '{character_id}' not found")
        CharacterPersistenceService.delete_character_data(character_id)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Character with id '{character_id}' not found")
    except HTTPException as e:
        # Preserve intended HTTP status codes
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Character deletion failed: {str(e)}")
