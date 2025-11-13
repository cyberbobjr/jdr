"""
FastAPI router for character creation V2.
Exposes the necessary routes for the new simplified character system using CharacterV2 models.
"""

from fastapi import APIRouter, HTTPException, Body, status
from uuid import uuid4
from datetime import datetime
from typing import List, Dict, Any

from back.models.domain.character_v2 import CharacterV2, Stats, Skills
from back.services.character_persistence_service import CharacterPersistenceService
from back.models.domain.races_manager import RacesManager
from back.models.domain.stats_manager import StatsManager
from back.models.domain.skills_manager import SkillsManager
from back.models.domain.equipment_manager import EquipmentManager
from back.models.schema import RaceData # Import RaceData and CultureData

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

class CreateCharacterV2Response(BaseModel):
    """Response model for character creation"""
    character_id: str = Field(..., description="Unique character identifier")
    status: str = Field(..., description="Creation status")
    created_at: str = Field(..., description="Creation timestamp")

class UpdateCharacterV2Request(BaseModel):
    """Request model for updating a V2 character"""
    character_id: str = Field(..., description="Character ID")
    name: str = Field(default="", description="Character name")
    stats: Dict[str, int] = Field(default={}, description="Character stats")
    skills: Dict[str, int] = Field(default={}, description="Character skills")
    background: str = Field(default="", description="Character background")

class UpdateCharacterV2Response(BaseModel):
    """Response model for character update"""
    character: Dict[str, Any] = Field(..., description="Updated character data")
    status: str = Field(..., description="Update status")

class CharacterV2Response(BaseModel):
    """Response model for character data"""
    character: Dict[str, Any] = Field(..., description="Character data")
    status: str = Field(..., description="Operation status")

@router.get("/races", summary="List of races V2", response_model=List[RaceData])
def get_races():
    """
    Returns the complete list of available races for the V2 system.
    
    **Output**: List of RaceData objects (Pydantic models)
    **Documentation**: Each race includes characteristics, cultures, and bonuses
    """
    races_manager = RacesManager()
    races_data = races_manager.get_all_races()
    
    # FastAPI will automatically serialize RaceData Pydantic objects to JSON
    return races_data

@router.get("/skills", summary="Skills data V2", response_model=Dict)
def get_skills():
    """
    Returns the complete skills structure for the V2 system.
    
    **Output**: Dictionary with skill groups and individual skills
    **Documentation**: 6 skill groups (combat, general, stealth, social, magic, crafting)
    """
    skills_manager = SkillsManager()
    return {
        "skills_for_llm": skills_manager.skills_data,
        "skill_groups": skills_manager.skill_groups
    }

@router.get("/equipment", summary="Equipment data V2", response_model=Dict)
def get_equipment():
    """
    Returns the complete equipment structure for the V2 system.
    
    **Output**: Dictionary with equipment categories and items
    **Documentation**: Weapons, armor, accessories, consumables with stats
    """
    equipment_manager = EquipmentManager()
    equipment_data = equipment_manager.get_all_equipment()
    
    # EquipmentManager already returns a dictionary
    return equipment_data

@router.get("/stats", summary="Stats data V2", response_model=Dict)
def get_stats():
    """
    Returns the complete stats structure for the V2 system.
    
    **Output**: Dictionary with stats definitions and bonus tables
    **Documentation**: 6 main attributes (strength, constitution, agility, intelligence, wisdom, charisma)
    """
    stats_manager = StatsManager()
    stats_data = stats_manager.get_all_stats_data()
    
    # StatsManager already returns a dictionary
    return stats_data

@router.post(
    "/create",
    response_model=CreateCharacterV2Response,
    summary="Create a new V2 character",
    description="Creates a new character using the simplified V2 system"
)
def create_character_v2(request: CreateCharacterV2Request):
    """
    Creates a new character using the V2 system with validation.
    - **Input**: Character creation data with stats, skills, race, culture
    - **Output**: character_id, status, creation timestamp
    """
    # Define custom exception for race validation
    class RaceNotFoundError(ValueError):
        pass

    try:
        # Generate unique character ID
        character_id = str(uuid4())
        now = datetime.now().isoformat()
        
        # Validate race and culture
        races_manager = RacesManager()
        race_data = races_manager.get_race_by_id(request.race_id)
        if not race_data:
            raise RaceNotFoundError(f"Race with id '{request.race_id}' not found")
        
        # Create character using V2 model
        # Create character dictionary directly for V2 model
        character_dict = {
            "id": character_id,
            "name": request.name,
            "race": request.race_id,
            "culture": request.culture_id,
            "stats": Stats(**request.stats).model_dump() if request.stats else Stats(strength=10, constitution=10, agility=10, intelligence=10, wisdom=10, charisma=10).model_dump(),
            "skills": Skills(**request.skills).model_dump() if request.skills else Skills().model_dump(),
            "combat_stats": {
                "max_hit_points": 50,
                "current_hit_points": 50,
                "max_mana_points": 30,
                "current_mana_points": 30,
                "armor_class": 10,
                "attack_bonus": 0
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
            "description": None
        }
        
        # Validate using CharacterV2 model
        character = CharacterV2(**character_dict)
        
        # Validate character using Pydantic
        character_dict = character.model_dump()
        
        # Save character data
        CharacterPersistenceService.save_character_data(character_id, character_dict)
        
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
def update_character_v2(request: UpdateCharacterV2Request):
    """
    Updates an existing V2 character with validation.
    - **Input**: character_id and updated fields
    - **Output**: Updated character data and status
    """
    # Define custom exception for character not found
    class CharacterNotFoundError(ValueError):
        pass
    
    try:
        # Load existing character
        existing_data = CharacterPersistenceService.load_character_data(request.character_id)
        if not existing_data:
            raise CharacterNotFoundError(f"Character with id '{request.character_id}' not found")
        
        # Update fields
        if request.name:
            existing_data['name'] = request.name
        if request.stats:
            existing_data['stats'] = Stats(**request.stats).model_dump()
        if request.skills:
            existing_data['skills'] = Skills(**request.skills).model_dump()
            
        existing_data['updated_at'] = datetime.now().isoformat()
        
        # Validate updated character using V2 model
        updated_character = CharacterV2(**existing_data)
        updated_dict = updated_character.model_dump()
        
        # Save updated character
        CharacterPersistenceService.save_character_data(request.character_id, updated_dict)
        
        return UpdateCharacterV2Response(
            character=updated_dict,
            status="updated"
        )
        
    except CharacterNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Character update failed: {str(e)}")

@router.get(
    "/character/{character_id}",
    response_model=CharacterV2Response,
    summary="Get V2 character",
    description="Retrieves a V2 character by ID"
)
def get_character_v2(character_id: str):
    """
    Retrieves a V2 character by ID.
    - **Input**: character_id
    - **Output**: Character data and status
    """
    try:
        character_data = CharacterPersistenceService.load_character_data(character_id)
        if not character_data:
            raise HTTPException(status_code=404, detail=f"Character with id '{character_id}' not found")
        
        # Validate character using V2 model
        character = CharacterV2(**character_data)
        
        return CharacterV2Response(
            character=character.model_dump(),
            status="loaded"
        )
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
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
def delete_character_v2(character_id: str):
    """
    Deletes a V2 character by ID.
    - **Input**: character_id
    - **Output**: 204 No Content if successful
    """
    try:
        CharacterPersistenceService.load_character_data(character_id)  # Verify character exists
        CharacterPersistenceService.delete_character_data(character_id)
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Character with id '{character_id}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Character deletion failed: {str(e)}")

@router.post(
    "/validate-character",
    summary="Validate V2 character",
    description="Validates a V2 character against game rules"
)
def validate_character_v2(character: Dict[str, Any] = Body(...)):
    """
    Validates a V2 character against game rules.
    - **Input**: Character data dictionary
    - **Output**: Validation results
    """
    try:
        # Validate character using V2 model
        validated_character = CharacterV2(**character)
        
        return {
            "valid": True,
            "character": validated_character.model_dump(),
            "message": "Character is valid"
        }
        
    except ValueError as e:
        return {
            "valid": False,
            "errors": [str(e)],
            "message": f"Validation failed: {str(e)}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")