"""
DTOs (Data Transfer Objects) pour les réponses API.
Standardise les formats de réponse pour tous les endpoints.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class CharacterListResponse(BaseModel):
    """
    Réponse standardisée pour la liste des personnages.
    """
    characters: List["Character"]


class CharacterDetailResponse(BaseModel):
    """
    Réponse standardisée pour les détails d'un personnage.
    """
    id: str
    name: Optional[str] = None
    race: Optional[str] = None
    culture: Optional[str] = None
    status: Optional[str] = None
    xp: int = 0
    gold: float = 0.0
    hp: int = 100
    caracteristiques: Optional[Dict[str, int]] = None
    competences: Optional[Dict[str, int]] = None
    inventory: Optional[List[Dict[str, Any]]] = None
    equipment: Optional[List[str]] = None
    spells: Optional[List[str]] = None
    culture_bonuses: Optional[Dict[str, int]] = None
    physical_description: Optional[str] = None


class ErrorResponse(BaseModel):
    """
    Réponse standardisée pour les erreurs.
    """
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = datetime.now()


class SuccessResponse(BaseModel):
    """
    Réponse standardisée pour les opérations réussies.
    """
    status: str = "success"
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()


class CharacterOperationResponse(BaseModel):
    """
    Réponse standardisée pour les opérations sur les personnages.
    """
    status: str
    character_id: str
    operation: str
    result: Dict[str, Any]
    timestamp: datetime = datetime.now()
