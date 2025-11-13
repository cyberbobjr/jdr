from __future__ import annotations

from fastapi import APIRouter
from typing import List
from back.models.domain.character_v2 import CharacterV2
from back.services.character_data_service import CharacterDataService
from back.utils.exceptions import CharacterNotFoundError, InternalServerError
from back.utils.logger import log_debug

router = APIRouter(tags=["characters"])


@router.get("/", response_model=List[CharacterV2])
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


@router.get("/{character_id}", response_model=CharacterV2)
async def get_character_detail(character_id: str):
    """
    Retrieve detailed information of a character by their unique identifier.

    This endpoint allows obtaining all detailed information of a specific character.

    Parameters:
        character_id (str): The unique identifier of the character to retrieve
    Returns:
        CharacterV2: The detailed information of the character
    """
    log_debug("Endpoint call characters/get_character_detail", character_id=str(character_id))

    try:
        data_service = CharacterDataService()
        character = data_service.get_character_by_id(character_id)

        log_debug("Character retrieved successfully",
                  action="get_character_detail_success",
                  character_id=character_id)

        return character

    except FileNotFoundError as e:
        log_debug("Character not found",
                  action="get_character_detail_not_found",
                  character_id=character_id,
                  error=str(e))
        raise CharacterNotFoundError(character_id)

    except Exception as e:
        log_debug("Error retrieving character",
                  action="get_character_detail_error",
                  character_id=character_id,
                  error=str(e))
        raise InternalServerError(f"Error retrieving character: {str(e)}")
