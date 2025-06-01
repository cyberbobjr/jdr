from pydantic import BaseModel
from uuid import UUID
from typing import Dict, List, Optional

class Item(BaseModel):
    id: str
    name: str
    weight: float
    base_value: float

class Character(BaseModel):
    id: UUID
    name: str
    race: str
    culture: str
    profession: str
    caracteristiques: Dict[str, int]
    competences: Dict[str, int]
    hp: int = 100  # calculé à partir de Constitution
    inventory: List[Item] = []
    equipment: List[str] = []
    spells: List[str] = []
    equipment_summary: Optional[Dict[str, float]] = None
    culture_bonuses: Optional[Dict[str, int]] = None

class ScenarioStatus(BaseModel):
    name: str
    status: str # Ex: "available", "in_progress", "completed"
    session_id: Optional[UUID] = None

class ScenarioList(BaseModel):
    scenarios: List[ScenarioStatus]

class CharacterList(BaseModel):
    characters: List[Character]
