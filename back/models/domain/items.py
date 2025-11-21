"""
Domain models for items and equipment.
"""
from typing import Optional
from pydantic import BaseModel

class EquipmentItem(BaseModel):
    """Standardized equipment item model"""
    id: str
    name: str
    category: str
    cost_gold: int = 0
    cost_silver: int = 0
    cost_copper: int = 0
    weight: float
    quantity: int
    equipped: bool
    description: Optional[str] = None
    damage: Optional[str] = None
    range: Optional[str] = None
    protection: Optional[int] = None
    type: Optional[str] = None
