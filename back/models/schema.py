from pydantic import BaseModel
from uuid import UUID
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from enum import Enum

# Import conditionnel pour éviter les imports circulaires
if TYPE_CHECKING:
    from back.models.domain.character_v2 import CharacterV2 as Character

class ItemType(str, Enum):
    """Types d'objets possibles"""
    MATERIEL = "Materiel"
    ARME = "Arme" 
    ARMURE = "Armure"
    NOURRITURE = "Nourriture"
    OBJET_MAGIQUE = "Objet_Magique"

class CharacterStatus(str, Enum):
    """Statuts possibles pour un personnage"""
    IN_PROGRESS = "en_cours"
    DONE = "complet"
    ARCHIVE = "archive"

class Item(BaseModel):
    """Modèle pour un objet d'inventaire avec toutes ses propriétés"""
    id: str  # Identifiant unique de l'instance de l'objet
    name: str  # Nom de l'objet (ex: "Coutelas")
    item_type: ItemType  # Type d'objet (Arme, Armure, Materiel, etc.)
    price_pc: float  # Prix en pièces de cuivre (support des décimales)
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
    """Modèle pour une partie de message dans l'historique de conversation"""
    content: str
    timestamp: str
    dynamic_ref: Optional[str] = None
    part_kind: str  # ex: "system-prompt", "user-prompt", "text", "tool-call", "tool-return"

class MessageUsage(BaseModel):
    """Modèle pour les informations d'usage des tokens"""
    requests: int
    request_tokens: int
    response_tokens: int
    total_tokens: int
    details: Optional[Dict[str, Any]] = None

class ConversationMessage(BaseModel):
    """Modèle pour un message complet dans l'historique de conversation"""
    parts: List[MessagePart]
    instructions: Optional[str] = None
    kind: str  # ex: "request", "response"
    usage: Optional[MessageUsage] = None
    model_name: Optional[str] = None
    timestamp: Optional[str] = None
    vendor_details: Optional[Any] = None
    vendor_id: Optional[str] = None

class PlayScenarioRequest(BaseModel):
    """Modèle de requête pour l'endpoint /scenarios/play"""
    message: str

# Modèles de réponse pour les autres endpoints scenarios

class SessionInfo(BaseModel):
    """Modèle pour les informations d'une session active"""
    session_id: str
    scenario_name: str
    character_id: str
    character_name: str

class ActiveSessionsResponse(BaseModel):
    """Modèle de réponse pour l'endpoint /scenarios/sessions"""
    sessions: List[SessionInfo]

class StartScenarioRequest(BaseModel):
    """Modèle de requête pour l'endpoint /scenarios/start"""
    scenario_name: str
    character_id: str

class StartScenarioResponse(BaseModel):
    """Modèle de réponse pour l'endpoint /scenarios/start"""
    session_id: str
    scenario_name: str
    character_id: str
    message: str
    llm_response: str

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
    """Schéma pour une caractéristique individuelle"""
    short_name: str
    category: str  # 'physical', 'mental', ou 'social'
    description: str
    examples: List[str]

class CharacteristicsResponse(BaseModel):
    """Schéma de réponse pour le endpoint /api/creation/characteristics"""
    characteristics: Dict[str, CharacteristicSchema]
    bonus_table: Dict[str, int]
    cost_table: Dict[str, int]
    starting_points: int

# Les modèles RaceData et CultureData sont maintenant définis plus haut et remplacent RaceSchema et CultureSchema

class UpdateSkillsRequest(BaseModel):
    character_id: str
    skills: Dict[str, int]

class UpdateSkillsResponse(BaseModel):
    status: str

# === Schémas pour la gestion d'équipement ===

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
    amount: float  # Positif pour ajouter, négatif pour retirer

class UpdateMoneyResponse(BaseModel):
    status: str
    gold: float

# === Schémas pour les compétences ===

class SkillStatBonus(BaseModel):
    """Modèle pour les bonus de statistiques sur une compétence"""
    min_value: int
    bonus_points: int

class SkillInfo(BaseModel):
    """Modèle pour les informations d'une compétence individuelle"""
    id: str
    name: str
    description: str
    stat_bonuses: Optional[Dict[str, SkillStatBonus]] = None

class SkillGroup(BaseModel):
    """Modèle pour un groupe de compétences"""
    name: str
    skills: Dict[str, SkillInfo]

class RacialAffinity(BaseModel):
    """Modèle pour une affinité raciale"""
    skill: str
    base_points: int

class SkillsResponse(BaseModel):
    """Modèle de réponse pour l'endpoint /api/creation/skills"""
    skill_groups: Dict[str, SkillGroup]
    racial_affinities: Dict[str, List[RacialAffinity]]

class EquipmentItem(BaseModel):
    """Modèle pour un élément d'équipement standardisé"""
    id: str
    name: str
    category: str
    cost: float
    weight: float
    quantity: int
    equipped: bool
    description: Optional[str] = None
    damage: Optional[str] = None
    range: Optional[str] = None
    protection: Optional[int] = None
    type: Optional[str] = None

class EquipmentResponse(BaseModel):
    """Modèle de réponse pour l'endpoint /api/creation/equipment"""
    weapons: List[EquipmentItem]
    armor: List[EquipmentItem]
    accessories: List[EquipmentItem]
    consumables: List[EquipmentItem]

class StatInfo(BaseModel):
    """Modèle pour les informations d'une statistique"""
    id: str
    name: str
    description: str
    min_value: int
    max_value: int

class ValueRange(BaseModel):
    """Modèle pour la plage de valeurs des statistiques"""
    min: int
    max: int

class StatsResponse(BaseModel):
    """Modèle de réponse pour l'endpoint /api/creation/stats"""
    stats: Dict[str, StatInfo]
    value_range: ValueRange
    bonus_formula: str
    bonus_table: Dict[str, int]
    cost_table: Dict[str, int]
    starting_points: Optional[int] = None
