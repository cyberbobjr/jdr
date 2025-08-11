"""
FastAPI router for character creation.
Exposes the necessary routes for each creation step and status tracking.
"""
from fastapi import APIRouter, HTTPException, Body, status
from uuid import uuid4
from datetime import datetime
from typing import List
import random

from back.models.domain.character import Character
from ..services.character_creation_service import CharacterCreationService
from back.services.character_persistence_service import CharacterPersistenceService
from back.models.domain.races_manager import RacesManager
from back.models.schema import (
    AllocateAttributesRequest, AllocateAttributesResponse, CharacterStatus,
    CheckAttributesRequest, CheckAttributesResponse,
    SaveCharacterRequest, SaveCharacterResponse,
    CheckSkillsRequest, CheckSkillsResponse,
    CreationStatusResponse,
    RaceData,
    StatsResponse, UpdateSkillsRequest, UpdateSkillsResponse,
    AddEquipmentRequest, AddEquipmentResponse,
    RemoveEquipmentRequest, RemoveEquipmentResponse,
    UpdateMoneyRequest, UpdateMoneyResponse
)
from back.agents.gm_agent_pydantic import enrich_user_message_with_character

router = APIRouter(tags=["creation"])

@router.get("/races", summary="List of races", response_model=List[RaceData])
def get_races():
    """
    Returns the complete list of available races (typed RaceData structure for Swagger documentation).
    **Output**: List of RaceData objects (complete structure from JSON).
    """
    races_manager = RacesManager()
    return races_manager.get_all_races()

@router.get(
    "/skills",
    summary="Detailed skills (LLM)",
    response_model=dict,
    response_description="Complete structure of the skills_for_llm.json file (groups, skills, difficulty levels, etc.)"
)
def get_skills():
    """
    Returns the complete structure of the skills_for_llm.json file (groups, skills, difficulty levels, etc.).
    **Output**: Dictionary conforming to skills_for_llm.json
    """
    return CharacterCreationService.get_skills()


@router.get("/equipments", summary="List of equipments", response_model=list)
def get_equipments():
    """
    Returns the list of available equipment.
    **Output**: List of strings (equipment)
    """
    return CharacterCreationService.get_equipments()

@router.get("/equipments-detailed", summary="Equipment with details", response_model=dict)
def get_equipments_detailed():
    """
    Returns the complete structure of equipment with their details (weapons, armor, items).
    **Output**: Complete dictionary of equipment grouped by category
    """
    from back.models.domain.equipment_manager import EquipmentManager
    equipment_manager = EquipmentManager()
    return equipment_manager.get_all_equipment()

@router.get("/spells", summary="List of spells", response_model=list)
def get_spells():
    """
    Returns the list of available spells.
    **Output**: List of strings (spells)
    """
    return CharacterCreationService.get_spells()

@router.post(
    "/allocate-attributes",
    response_model=AllocateAttributesResponse,
    summary="Automatic attribute allocation",
    description="Automatically allocates attributes according to the provided race."
)
def allocate_attributes(request: AllocateAttributesRequest):
    """
    Automatically allocates attributes according to the race.
    - **Input**: race_id (str)
    - **Output**: Dictionary of allocated attributes
    """
    races_manager = RacesManager()
    race_data = races_manager.get_race_by_id(request.race_id)
    if not race_data:
        raise HTTPException(status_code=404, detail=f"Race with id '{request.race_id}' not found")
    
    attributes = CharacterCreationService.allocate_attributes_auto(race_data)
    return AllocateAttributesResponse(attributes=attributes)

@router.post(
    "/check-attributes",
    response_model=CheckAttributesResponse,
    summary="Attribute validation",
    description="Checks that the distribution of attribute points respects the game rules."
)
def check_attributes(request: CheckAttributesRequest):
    """
    Checks that the attribute points respect the rules (budget, bounds).
    - **Input**: attributes (dict)
    - **Output**: valid (bool)
    """
    valid = CharacterCreationService.check_attributes_points(request.attributes)
    return CheckAttributesResponse(valid=valid)

@router.post(
    "/new",
    response_model=CreationStatusResponse,
    summary="Create a new character",
    description="Creates a new character (initial state, id and creation date)."
)
def create_new_character():
    """
    Creates a new character (initial state, id and creation date).
    - **Output**: character_id (str), created_at (str), status (str)
    """
    character_id = str(uuid4())
    now = datetime.now().isoformat()
    starting_money = random.randint(1, 50)
    
    character_data = {
        "id": character_id,
        "created_at": now,
        "last_update": now,
        "current_step": "creation",
        "status": CharacterStatus.IN_PROGRESS,
        "xp": 0, 
        "gold": starting_money
    }
    CharacterPersistenceService.save_character_data(character_id, character_data)
    return {"id": character_id, "created_at": now, "status": CharacterStatus.IN_PROGRESS}

@router.post(
    "/save",
    response_model=SaveCharacterResponse,
    summary="Save character",
    description="Saves or updates the data of the character being created."
)
def save_character(request: SaveCharacterRequest):
    """
    Saves or updates the data of the character being created.
    - **Input**: character_id (str), character (dict)
    - **Output**: status (str)
    """
    character = CharacterPersistenceService.save_character_data(request.character_id, request.character)
    if Character.is_character_finalized(character) and character.get("status") == CharacterStatus.IN_PROGRESS:
        character["status"] = CharacterStatus.DONE
        character["last_update"] = datetime.now().isoformat()
        character = CharacterPersistenceService.save_character_data(request.character_id, character)

    return SaveCharacterResponse(status=character.get("status"), character=character)

@router.get(
    "/status/{character_id}",
    response_model=CreationStatusResponse,
    summary="Character creation status",
    description="Returns the creation status of the character (in progress, finished, not found)."
)
def get_creation_status(character_id: str):
    """
    Returns the creation status of the character (in progress, finished, not found).
    - **Input**: character_id (str)
    - **Output**: status (str)
    """
    try:
        data = CharacterPersistenceService.load_character_data(character_id)
        return CreationStatusResponse(character_id=character_id, status=data.get("status", "in_progress"))
    except FileNotFoundError:
        return CreationStatusResponse(character_id=character_id, status="not_found")

@router.post(
    "/check-skills",
    response_model=CheckSkillsResponse,
    summary="Skill validation",
    description="Checks that the distribution of skill points respects the rules (budget, favorite groups, max per skill)."
)
def check_skills(request: CheckSkillsRequest):
    """
    Checks that the distribution of skill points respects the rules (budget, favorite groups, max per skill).
    - **Input**: skills (dict)
    - **Output**: valid (bool), cost (int)
    """
    valid = CharacterCreationService.check_skills_points(request.skills)
    cost = CharacterCreationService.calculate_skills_cost(request.skills)
    return CheckSkillsResponse(valid=valid, cost=cost)

@router.post("/generate-name", summary="Generate 5 character names via LLM")
async def generate_character_name(character: dict = Body(...)):
    """
    Generates 5 appropriate character names via the LLM agent, based on the partial character sheet.
    **Input**: Partial character sheet
    **Output**: List of 5 generated names
    """
    try:
        from back.agents.gm_agent_pydantic import build_simple_gm_agent
        agent = build_simple_gm_agent()
        prompt = enrich_user_message_with_character(
            "Suggest 5 appropriate character names for this sheet. Respond with a numbered list (1. Name1, 2. Name2, etc.).",
            character
        )
        result = await agent.run(prompt)
        names = []
        for line in result.output.strip().split('\n'):
            if line.strip() and (line.strip().startswith(('1.', '2.', '3.', '4.', '5.')) or line.strip()[0].isdigit()):
                name = line.split('.', 1)[-1].strip()
                if name:
                    names.append(name)
        
        if len(names) < 5:
            generic_names = ["Aragorn", "Legolas", "Gimli", "Boromir", "Faramir"]
            names.extend(generic_names[len(names):5])
        
        return {"names": names[:5]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-background", summary="Generate 5 character backgrounds via LLM")
async def generate_character_background(character: dict = Body(...)):
    """
    Generates 5 story backgrounds for the character via the LLM agent.
    **Input**: Partial character sheet
    **Output**: List of 5 generated backgrounds
    """
    try:
        from back.agents.gm_agent_pydantic import build_simple_gm_agent
        agent = build_simple_gm_agent()
        prompt = enrich_user_message_with_character(
            """
            Write 5 immersive and coherent story backgrounds for this character. 
            Each background should include a life goal for the character. 
            Respond with a numbered list (1. Background1, 2. Background2, etc.). 
            Each background should be 6-7 sentences long.
            """,
            character
        )
        result = await agent.run(prompt)
        backgrounds = []
        current_background = ""
        
        for line in result.output.strip().split('\n'):
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or (line[0].isdigit() and '.' in line)):
                if current_background:
                    backgrounds.append(current_background.strip())
                current_background = line.split('.', 1)[-1].strip()
            elif line and current_background:
                current_background += " " + line
        
        if current_background:
            backgrounds.append(current_background.strip())
        
        if len(backgrounds) < 5:
            generic_backgrounds = [
                "An experienced adventurer who has traveled many lands.",
                "A hero in the making seeking to prove his worth.",
                "A wise man with an ancient knowledge of traditions.",
                "A brave warrior defending the innocent.",
                "A curious explorer discovering the mysteries of the world."
            ]
            backgrounds.extend(generic_backgrounds[len(backgrounds):5])
        
        return {"backgrounds": backgrounds[:5]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-physical-description", summary="Generate 5 physical descriptions via LLM")
async def generate_character_physical_description(character: dict = Body(...)):
    """
    Generates 5 physical descriptions for the character via the LLM agent.
    **Input**: Partial character sheet
    **Output**: List of 5 generated physical descriptions
    """
    try:
        from back.agents.gm_agent_pydantic import build_simple_gm_agent
        agent = build_simple_gm_agent()
        prompt = enrich_user_message_with_character(
            """
            Describe 5 different physical appearances for this character in detail. 
            You must provide a precise description of the character (face, body, clothes) in order to generate a prompt for an image generator. 
            Be factual, do not give impressions or feelings, use descriptive terms, as if you were describing a character to a blind person.
            Respond with a numbered list (1. Description1, 2. Description2, etc.).
            Each description should be 6-7 sentences long.
            """,
            character
        )
        result = await agent.run(prompt)
        descriptions = []
        current_description = ""
        
        for line in result.output.strip().split('\n'):
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.')) or (line[0].isdigit() and '.' in line)):
                if current_description:
                    descriptions.append(current_description.strip())
                current_description = line.split('.', 1)[-1].strip()
            elif line and current_description:
                current_description += " " + line
        
        if current_description:
            descriptions.append(current_description.strip())
        
        if len(descriptions) < 5:
            generic_descriptions = [
                "A person with fine and elegant features, with piercing eyes and a noble posture.",
                "A robust and imposing individual, with calloused hands testifying to a life of labor.",
                "A slender and graceful figure, moving with natural agility.",
                "A face marked by experience, with wrinkles that tell a thousand stories.",
                "A mysterious and captivating appearance, with a gaze that seems to pierce souls."
            ]
            descriptions.extend(generic_descriptions[len(descriptions):5])
        
        return {"physical_descriptions": descriptions[:5]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", summary="Complete stats data", response_model=StatsResponse)
def get_stats():
    """
    Returns the complete stats.json file with all data:
    - Definitions of stats (Strength, Agility, etc.)
    - Bonus table by value
    - Point cost table
    - Starting points
    **Output**: Complete content of the stats.json file
    """
    from back.models.domain.stats_manager import StatsManager
    manager = StatsManager()
    return manager.get_all_stats_data()

@router.delete("/delete/{character_id}", summary="Delete a character", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(character_id: str):
    """
    Deletes a character from their ID.
    **Input**: character_id (str)
    **Output**: 204 No Content if successful
    """
    from back.services.character_persistence_service import CharacterPersistenceService
    CharacterPersistenceService.delete_character_data(character_id)
    return None

@router.post(
    "/update-skills",
    response_model=UpdateSkillsResponse,
    summary="Update skills",
    description="Updates only the skills of the character being created."
)
def update_skills(request: UpdateSkillsRequest):
    """
    Updates only the skills of the character being created.
    Performs a merge with existing data.
    - **Input**: character_id (str), skills (dict)
    - **Output**: status (str)
    """
    character_data = {"skills": request.skills}
    CharacterPersistenceService.save_character_data(request.character_id, character_data)
    return UpdateSkillsResponse(status="in_progress")

# === Routes for equipment management ===

@router.post(
    "/add-equipment",
    response_model=AddEquipmentResponse,
    summary="Add equipment",
    description="Adds equipment to the character and deducts the corresponding money."
)
def add_equipment(request: AddEquipmentRequest):    
    """
    Adds equipment to the character and deducts the corresponding money.
    - **Input**: character_id (str), equipment_name (str)
    - **Output**: status (str), gold (int), total_weight (float), equipment_added (dict)
    """
    try:
        character_data = CharacterPersistenceService.load_character_data(request.character_id)
        
        from back.models.domain.equipment_manager import EquipmentManager
        
        equipment_manager = EquipmentManager()
        equipment_details = equipment_manager.get_equipment_by_name(request.equipment_name)
        
        if not equipment_details:
            raise ValueError(f"Equipment '{request.equipment_name}' not found")
        current_gold = character_data.get('gold', 0.0)
        equipment_cost = equipment_details.get('cost', 0)
        
        if current_gold < equipment_cost:
            raise ValueError("Not enough money to buy this equipment")
        
        inventory = character_data.get('inventory', [])
        equipment_already_exists = any(
            item.get('name') == request.equipment_name for item in inventory
        )
        
        if not equipment_already_exists:
            import uuid
            
            equipment_type = equipment_details.get('type', 'material').lower()
            if equipment_type == 'weapon':
                item_type = 'Weapon'
            elif equipment_type == 'armor':
                item_type = 'Armor'
            elif equipment_type == 'food':
                item_type = 'Food'
            elif equipment_type == 'magic_item':
                item_type = 'Magic_Item'
            else:
                item_type = 'Material'
            
            new_item = {
                "id": str(uuid.uuid4()),
                "name": request.equipment_name,
                "item_type": item_type,
                "price_pc": equipment_details.get('cost', 0),
                "weight_kg": equipment_details.get('weight', 0),
                "description": equipment_details.get('description', ''),
                "category": equipment_details.get('category'),
                "damage": equipment_details.get('damage'),
                "quantity": 1,
                "is_equipped": False
            }
            inventory.append(new_item)
        
        new_gold = current_gold - equipment_cost
        
        total_weight = sum(item.get('weight_kg', 0) * item.get('quantity', 1) for item in inventory)
        
        character_data['inventory'] = inventory
        character_data['gold'] = new_gold
        
        CharacterPersistenceService.save_character_data(request.character_id, character_data)
        return AddEquipmentResponse(
            status='success',
            gold=new_gold,
            total_weight=total_weight,
            equipment_added=equipment_details
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Character not found")

@router.post(
    "/remove-equipment",
    response_model=RemoveEquipmentResponse,
    summary="Remove equipment",
    description="Removes equipment from the character and refunds the corresponding money."
)
def remove_equipment(request: RemoveEquipmentRequest):   
    """
    Removes equipment from the character and refunds the corresponding money.
    - **Input**: character_id (str), equipment_name (str)
    - **Output**: status (str), gold (int), total_weight (float), equipment_removed (dict)
    """
    try:
        character_data = CharacterPersistenceService.load_character_data(request.character_id)
        
        from back.models.domain.equipment_manager import EquipmentManager
        
        equipment_manager = EquipmentManager()
        equipment_details = equipment_manager.get_equipment_by_name(request.equipment_name)
        
        if not equipment_details:
            raise ValueError(f"Equipment '{request.equipment_name}' not found")
        inventory = character_data.get('inventory', [])
        
        item_to_remove = None
        for item in inventory:
            if item.get('name') == request.equipment_name:
                item_to_remove = item
                break
        
        if not item_to_remove:
            raise ValueError(f"Equipment '{request.equipment_name}' is not in the inventory")
            
        inventory.remove(item_to_remove)
        current_gold = character_data.get('gold', 0.0)
        equipment_cost = equipment_details.get('cost', 0)
        new_gold = current_gold + equipment_cost
        total_weight = sum(item.get('weight_kg', 0) * item.get('quantity', 1) for item in inventory)
        
        character_data['inventory'] = inventory
        character_data['gold'] = new_gold
        
        CharacterPersistenceService.save_character_data(request.character_id, character_data)
        return RemoveEquipmentResponse(
            status='success',
            gold=new_gold,
            total_weight=total_weight,
            equipment_removed=equipment_details
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Character not found")

@router.post(
    "/update-money",
    response_model=UpdateMoneyResponse,
    summary="Update money",
    description="Updates the character's money (positive to add, negative to remove)."
)
def update_money(request: UpdateMoneyRequest):    
    """
    Updates the character's money.
    - **Input**: character_id (str), amount (int)
    - **Output**: status (str), gold (int)
    """
    try:
        character_data = CharacterPersistenceService.load_character_data(request.character_id)
        
        current_gold = character_data.get('gold', 0.0)
        new_gold = max(0.0, current_gold + request.amount)
        
        character_data['gold'] = new_gold
        
        CharacterPersistenceService.save_character_data(request.character_id, character_data)
        return UpdateMoneyResponse(
            status='success',
            gold=new_gold
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Character not found")
