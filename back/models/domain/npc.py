"""NPC domain model."""
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from .character import Stats, Skills, Equipment, CombatStats, Spells


class NPC(BaseModel):
    """Simplified NPC model mirroring the Character data contract."""
    id: UUID = Field(default_factory=uuid4, description="Unique NPC identifier")
    name: str = Field(..., min_length=1, max_length=100, description="NPC name")
    description: Optional[str] = Field(default=None, max_length=1000, description="NPC description")
    
    # Core stats (simplified for NPCs, can be derived from archetype)
    stats: Stats = Field(..., description="NPC base statistics")
    
    # Skills (simplified for NPCs, focus on combat/relevant skills)
    skills: Skills = Field(default_factory=Skills, description="NPC skills")
    
    # Equipment (simplified for NPCs, focus on combat gear)
    equipment: Equipment = Field(default_factory=Equipment, description="NPC equipment")
    
    # Combat stats (crucial for encounters)
    combat_stats: CombatStats = Field(..., description="NPC combat statistics")
    
    # Spells (if the NPC is a spellcaster)
    spells: Spells = Field(default_factory=Spells, description="NPC known spells")
    
    # Additional NPC-specific fields
    archetype: str = Field(..., description="Type of NPC (e.g., 'Goblin Warrior', 'Forest Elf Archer')")
    level: int = Field(default=1, ge=1, le=20, description="NPC challenge level")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "Goblin Grunt",
                "description": "A small, green-skinned goblin with a rusty sword.",
                "archetype": "Goblin Warrior",
                "level": 1,
                "stats": {
                    "strength": 10,
                    "constitution": 10,
                    "agility": 12,
                    "intelligence": 8,
                    "wisdom": 10,
                    "charisma": 6
                },
                "skills": {
                    "combat": {"rusty_sword": 2},
                    "general": {"perception": 1}
                },
                "equipment": {
                    "weapons": [{"name": "rusty_sword", "damage": "1d6", "weight": 2}],
                    "armor": [{"name": "leather_scrap_armor", "defense": 1, "weight": 5}]
                },
                "combat_stats": {
                    "max_hit_points": 15,
                    "current_hit_points": 15,
                    "armor_class": 13,
                    "attack_bonus": 2
                },
                "spells": {}
            }
        }

__all__ = ['NPC']