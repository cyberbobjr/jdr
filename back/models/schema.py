from pydantic import BaseModel
from uuid import UUID
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from enum import Enum
from back.models.enums import CharacterStatus, ItemType
from back.models.domain.items import EquipmentItem

# Import conditionnel pour éviter les imports circulaires
if TYPE_CHECKING:
    from back.models.domain.character import Character

class LLMConfig(BaseModel):
    """Configuration for LLM provider"""
    api_endpoint: str
    api_key: str
    model: str



class Item(BaseModel):
    """Model for an inventory item with all its properties"""
    id: str  # Unique identifier of the item instance
    name: str  # Item name (e.g., "Dagger")
    item_type: ItemType  # Item type (Weapon, Armor, Material, etc.)
    price_pc: float  # Price in copper pieces (supports decimals)
    weight_kg: float  # Poids en kilogrammes
    description: str  # Description de l'objet
    category: Optional[str] = None  # Catégorie spécifique (ex: "Couteau", "Cuir", etc.)
    
    # Propriétés spécifiques aux armes
    damage: Optional[str] = None  # Dégâts de l'arme (ex: "1d6+2")
    
    # Propriétés spécifiques aux armures
    protection: Optional[int] = None  # Points de protection de l'armure
    armor_type: Optional[str] = None  # Type d'armure (Cuir, Maille, Plates, etc.)
    
    # Propriétés générales
    quantity: int = 1  # Quantité possédée de cet objet
    is_equipped: bool = False  # Si l'objet est actuellement équipé
    
    # Métadonnées
    crafting_time: Optional[str] = None  # Temps de fabrication
    special_properties: Optional[List[str]] = None  # Propriétés spéciales

class RaceData(BaseModel):
    id: str
    name: str
    characteristic_bonuses: Dict[str, int]
    special_abilities: Optional[List[str]] = []
    base_languages: List[str]
    optional_languages: List[str]
    cultures: Optional[List['CultureData']] = None

class CultureData(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    skill_bonuses: Optional[Dict[str, int]] = None
    characteristic_bonuses: Optional[Dict[str, int]] = None
    free_skill_points: Optional[int] = None
    traits: Optional[str] = None
    special_traits: Optional[Dict[str, Any]] = None

class ScenarioStatus(BaseModel):
    name: str
    status: str # Ex: "available", "in_progress", "completed"
    session_id: Optional[UUID] = None
    scenario_name: Optional[str] = None  # Nom du scénario pour les sessions en cours
    character_name: Optional[str] = None  # Nom du personnage pour les sessions en cours

class ScenarioList(BaseModel):
    scenarios: List[ScenarioStatus]

class MessagePart(BaseModel):
    """Model for a message part in conversation history"""
    content: str
    timestamp: str
    dynamic_ref: Optional[str] = None
    part_kind: str  # e.g., "system-prompt", "user-prompt", "text", "tool-call", "tool-return"

class MessageUsage(BaseModel):
    """Model for token usage information"""
    requests: int
    request_tokens: int
    response_tokens: int
    total_tokens: int
    details: Optional[Dict[str, Any]] = None

class ConversationMessage(BaseModel):
    """Model for a complete message in conversation history"""
    parts: List[MessagePart]
    instructions: Optional[str] = None
    kind: str  # e.g., "request", "response"
    usage: Optional[MessageUsage] = None
    model_name: Optional[str] = None
    timestamp: Optional[str] = None
    vendor_details: Optional[Any] = None
    vendor_id: Optional[str] = None

class PlayScenarioRequest(BaseModel):
    """Request model for the merged /gamesession/play endpoint"""
    message: Optional[str] = None  # Optional for starting (uses default message)
    scenario_name: Optional[str] = None  # For starting a new session
    character_id: Optional[str] = None   # For starting a new session

# Response models for other scenario endpoints

class SessionInfo(BaseModel):
    """Model for active session information"""
    session_id: str
    scenario_name: str
    character_id: str
    character_name: str

class ActiveSessionsResponse(BaseModel):
    """Response model for the /scenarios/sessions endpoint"""
    sessions: List[SessionInfo]

class StartScenarioRequest(BaseModel):
    """Request model for the /scenarios/start endpoint"""
    scenario_name: str
    character_id: str

class StartScenarioResponse(BaseModel):
    """Response model for the /scenarios/start endpoint"""
    session_id: str
    scenario_name: str
    character_id: str
    message: str
    llm_response: str

class PlayScenarioResponse(BaseModel):
    """Response model for the /scenarios/play endpoint"""
    response: List[Dict[str, Any]]
    session_id: UUID

class ScenarioHistoryResponse(BaseModel):
    """Response model for the /scenarios/history/{session_id} endpoint"""
    history: List[Dict[str, Any]]

class DeleteMessageResponse(BaseModel):
    """Response model for the DELETE /scenarios/history/{session_id}/{message_index} endpoint"""
    message: str
    deleted_message_info: Dict[str, Any]
    remaining_messages_count: int

class AllocateAttributesRequest(BaseModel):
    race: str

class AllocateAttributesResponse(BaseModel):
    attributes: Dict[str, int]

class CheckAttributesRequest(BaseModel):
    attributes: Dict[str, int]

class CheckAttributesResponse(BaseModel):
    valid: bool

class SaveCharacterRequest(BaseModel):
    character_id: str
    character: dict

class SaveCharacterResponse(BaseModel):
    character: dict
    status: str

class CheckSkillsRequest(BaseModel):
    skills: Dict[str, int]

class CheckSkillsResponse(BaseModel):
    valid: bool
    cost: int

class CreationStatusResponse(BaseModel):
    id: str
    status: str
    created_at: Optional[str] = None

class CharacterListAny(BaseModel):
    characters: List[dict]

class CharacteristicSchema(BaseModel):
    """Schema for an individual characteristic"""
    short_name: str
    category: str  # 'physical', 'mental', or 'social'
    description: str
    examples: List[str]

class CharacteristicsResponse(BaseModel):
    """Response schema for the /api/creation/characteristics endpoint"""
    characteristics: Dict[str, CharacteristicSchema]
    bonus_table: Dict[str, int]
    cost_table: Dict[str, int]
    starting_points: int

# The RaceData and CultureData models are now defined above and replace RaceSchema and CultureSchema

class UpdateSkillsRequest(BaseModel):
    character_id: str
    skills: Dict[str, int]

class UpdateSkillsResponse(BaseModel):
    status: str

# === Schemas for equipment management ===

class AddEquipmentRequest(BaseModel):
    character_id: str
    equipment_name: str

class AddEquipmentResponse(BaseModel):
    status: str
    gold: float
    total_weight: float
    equipment_added: dict

class RemoveEquipmentRequest(BaseModel):
    character_id: str
    equipment_name: str

class RemoveEquipmentResponse(BaseModel):
    status: str
    gold: float
    total_weight: float
    equipment_removed: dict

class UpdateMoneyRequest(BaseModel):
    character_id: str
    amount: float  # Positive to add, negative to subtract

class UpdateMoneyResponse(BaseModel):
    status: str
    gold: float

# === Schemas for skills ===

class SkillStatBonus(BaseModel):
    """Model for stat bonuses on a skill"""
    min_value: int
    bonus_points: int

class SkillInfo(BaseModel):
    """Model for individual skill information"""
    id: str
    name: str
    description: str
    stat_bonuses: Optional[Dict[str, SkillStatBonus]] = None

class SkillGroup(BaseModel):
    """Model for a skill group"""
    name: str
    skills: Dict[str, SkillInfo]

class RacialAffinity(BaseModel):
    """Model for racial affinity"""
    skill: str
    base_points: int

class SkillsResponse(BaseModel):
    """Response model for the /api/creation/skills endpoint"""
    skill_groups: Dict[str, SkillGroup]
    racial_affinities: Dict[str, List[RacialAffinity]]



class EquipmentResponse(BaseModel):
    """Response model for the /api/creation/equipment endpoint"""
    weapons: List[EquipmentItem]
    armor: List[EquipmentItem]
    accessories: List[EquipmentItem]
    consumables: List[EquipmentItem]

class StatInfo(BaseModel):
    """Model for stat information"""
    id: str
    name: str
    description: str
    min_value: int
    max_value: int

class ValueRange(BaseModel):
    """Model for stat value range"""
    min: int
    max: int

class StatsResponse(BaseModel):
    """Response model for the /api/creation/stats endpoint"""
    stats: Dict[str, StatInfo]
    value_range: ValueRange
    bonus_formula: str
    bonus_table: Dict[str, int]
    cost_table: Dict[str, int]
    starting_points: Optional[int] = None
