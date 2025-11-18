"""Real-time combat state models."""
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator
from uuid import UUID, uuid4
from enum import Enum

from .character import Character
from .npc import NPC

class CombatantType(str, Enum):
    PLAYER = "player"
    NPC = "npc"

class Combatant(BaseModel):
    """
    Represents a participant in combat, either a player character or an NPC.
    """
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the combatant")
    name: str = Field(..., description="Name of the combatant")
    type: CombatantType = Field(..., description="Type of combatant (player or NPC)")
    
    # Current combat stats (can be a subset or reference to Character/NPC combat_stats)
    current_hit_points: int = Field(..., ge=0, description="Current hit points")
    max_hit_points: int = Field(..., ge=1, description="Maximum hit points")
    armor_class: int = Field(..., ge=1, description="Armor Class")
    initiative_roll: int = Field(..., description="Result of the initiative roll")
    
    # Reference to the full character/NPC data (optional, for detailed info)
    character_ref: Optional[Character] = Field(default=None, description="Full Character data if player")
    npc_ref: Optional[NPC] = Field(default=None, description="Full NPC data if NPC")

    @model_validator(mode='after')
    def validate_combatant_type_reference(self) -> 'Combatant':
        if self.type == CombatantType.PLAYER and not self.character_ref:
            raise ValueError("Player combatant must have a character_ref")
        if self.type == CombatantType.NPC and not self.npc_ref:
            raise ValueError("NPC combatant must have an npc_ref")
        if self.type == CombatantType.PLAYER and self.npc_ref:
            raise ValueError("Player combatant cannot have an npc_ref")
        if self.type == CombatantType.NPC and self.character_ref:
            raise ValueError("NPC combatant cannot have a character_ref")
        return self

    def is_alive(self) -> bool:
        return self.current_hit_points > 0

    def take_damage(self, amount: int) -> int:
        old_hp = self.current_hit_points
        self.current_hit_points = max(0, self.current_hit_points - amount)
        return old_hp - self.current_hit_points

    def heal(self, amount: int) -> int:
        old_hp = self.current_hit_points
        self.current_hit_points = min(self.current_hit_points + amount, self.max_hit_points)
        return self.current_hit_points - old_hp

class CombatState(BaseModel):
    """
    Represents the real-time state of a combat encounter.
    """
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for this combat instance")
    participants: List[Combatant] = Field(..., description="List of all combatants in the encounter")
    turn_order: List[UUID] = Field(default_factory=list, description="Ordered list of combatant IDs for turns")
    current_turn_combatant_id: Optional[UUID] = Field(default=None, description="ID of the combatant whose turn it is")
    round_number: int = Field(default=1, ge=1, description="Current round number of the combat")
    is_active: bool = Field(default=True, description="True if combat is ongoing, False if ended")
    log: List[str] = Field(default_factory=list, description="Log of combat actions and events")

    @model_validator(mode='after')
    def validate_turn_order_participants(self) -> 'CombatState':
        participant_ids = {p.id for p in self.participants}
        if not all(turn_id in participant_ids for turn_id in self.turn_order):
            raise ValueError("Turn order contains IDs not present in participants list")
        if self.current_turn_combatant_id and self.current_turn_combatant_id not in participant_ids:
            raise ValueError("Current turn combatant ID not found in participants")
        return self

    def get_combatant(self, combatant_id: UUID) -> Optional[Combatant]:
        """Retrieve a combatant by their ID."""
        for p in self.participants:
            if p.id == combatant_id:
                return p
        return None

    def get_current_combatant(self) -> Optional[Combatant]:
        """Retrieve the combatant whose turn it is."""
        if self.current_turn_combatant_id:
            return self.get_combatant(self.current_turn_combatant_id)
        return None

    def add_log_entry(self, entry: str) -> None:
        """Add an event to the combat log."""
        self.log.append(f"Round {self.round_number} - {entry}")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "participants": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "Aragorn",
                        "type": "player",
                        "current_hit_points": 60,
                        "max_hit_points": 60,
                        "armor_class": 17,
                        "initiative_roll": 15
                    },
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174001",
                        "name": "Goblin Grunt",
                        "type": "npc",
                        "current_hit_points": 15,
                        "max_hit_points": 15,
                        "armor_class": 13,
                        "initiative_roll": 12
                    }
                ],
                "turn_order": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "123e4567-e89b-12d3-a456-426614174001"
                ],
                "current_turn_combatant_id": "123e4567-e89b-12d3-a456-426614174000",
                "round_number": 1,
                "is_active": True,
                "log": ["Combat started.", "Aragorn rolled 15 for initiative."]
            }
        }

__all__ = [
    'CombatState',
    'Combatant',
    'CombatantType'
]