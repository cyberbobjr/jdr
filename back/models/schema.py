from pydantic import BaseModel
from uuid import UUID
from typing import Dict, List, Optional, Any
from enum import Enum

class ItemType(str, Enum):
    """Types d'objets possibles"""
    MATERIEL = "Materiel"
    ARME = "Arme" 
    ARMURE = "Armure"
    NOURRITURE = "Nourriture"
    OBJET_MAGIQUE = "Objet_Magique"

class Item(BaseModel):
    """Modèle pour un objet d'inventaire avec toutes ses propriétés"""
    id: str  # Identifiant unique de l'instance de l'objet
    name: str  # Nom de l'objet (ex: "Coutelas")
    item_type: ItemType  # Type d'objet (Arme, Armure, Materiel, etc.)
    price_pc: int  # Prix en pièces de cuivre
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

class Character(BaseModel):
    id: UUID
    name: str
    race: str
    culture: str
    profession: str
    caracteristiques: Dict[str, int]
    competences: Dict[str, int]
    hp: int = 100  # calculé à partir de Constitution
    inventory: List[Item] = []  # Inventaire détaillé avec objets complets
    spells: List[str] = []
    equipment_summary: Optional[Dict[str, float]] = None
    culture_bonuses: Optional[Dict[str, int]] = None

class ScenarioStatus(BaseModel):
    name: str
    status: str # Ex: "available", "in_progress", "completed"
    session_id: Optional[UUID] = None
    scenario_name: Optional[str] = None  # Nom du scénario pour les sessions en cours
    character_name: Optional[str] = None  # Nom du personnage pour les sessions en cours

class ScenarioList(BaseModel):
    scenarios: List[ScenarioStatus]

class CharacterList(BaseModel):
    characters: List[Character]

class MessagePart(BaseModel):
    """Modèle pour une partie de message dans l'historique de conversation"""
    content: str
    timestamp: str
    dynamic_ref: Optional[str] = None
    part_kind: str  # ex: "system-prompt", "user-prompt", "text", "tool-call", "tool-return"

class ToolCall(BaseModel):
    """Modèle pour un appel d'outil dans l'historique"""
    tool_name: str
    args: str  # JSON stringifié
    tool_call_id: str
    part_kind: str = "tool-call"

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

class PlayScenarioResponse(BaseModel):
    """Modèle de réponse pour l'endpoint /scenarios/play"""
    response: List[ConversationMessage]

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

class ScenarioHistoryResponse(BaseModel):
    """Modèle de réponse pour l'endpoint /scenarios/history/{session_id}"""
    history: List[ConversationMessage]
