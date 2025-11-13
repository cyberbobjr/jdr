"""
New Strict Pydantic Character Model v2.0
Simplified English-only naming for character creation

This module provides a simplified character model with:
- 400 stat points instead of 550
- 40 skill development points instead of 84
- 6 main stat attributes
- 6 skill groups
- Strict Pydantic validation
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from uuid import UUID, uuid4
from datetime import datetime, timezone
from enum import Enum
 


class CharacterStatus(str, Enum):
    """Character lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    IN_GAME = "in_game"


class Stats(BaseModel):
    """
    Simplified statistics system
    6 main attributes with 400 total base points
    
    Point allocation rules:
    - Each stat ranges from 3 to 20
    - Total points must not exceed 400
    - Recommended distribution: 10-15 per stat for balanced characters
    """
    strength: int = Field(..., ge=3, le=20, description="Physical power and melee damage")
    constitution: int = Field(..., ge=3, le=20, description="Health points and endurance")
    agility: int = Field(..., ge=3, le=20, description="Speed, reflexes, and dodge")
    intelligence: int = Field(..., ge=3, le=20, description="Magical power and learning")
    wisdom: int = Field(..., ge=3, le=20, description="Perception and willpower")
    charisma: int = Field(..., ge=3, le=20, description="Social influence and leadership")
    
    @field_validator('*')
    @classmethod
    def validate_stat_range(cls, v: int) -> int:
        """Ensure each stat is within valid range"""
        if not (3 <= v <= 20):
            raise ValueError(f"Stat must be between 3 and 20, got {v}")
        return v
    
    # Removed total points validator: simplified rule is per-stat cap only
    
    def calculate_total_points(self) -> int:
        """Calculate total allocated points"""
        return sum([
            self.strength,
            self.constitution,
            self.agility,
            self.intelligence,
            self.wisdom,
            self.charisma
        ])
    
    def get_modifier(self, stat_name: str) -> int:
        """
        Calculate modifier for a given stat
        Simplified bonus table: (stat - 10) // 2
        """
        stat_value = getattr(self, stat_name.lower())
        return (stat_value - 10) // 2
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "strength": 14,
                "constitution": 16,
                "agility": 12,
                "intelligence": 13,
                "wisdom": 15,
                "charisma": 10
            }
        }
    )


class Skills(BaseModel):
    """
    Simplified skills system
    6 main groups with 40 total development points
    
    Skill rules:
    - Each skill rank costs 1 development point
    - Skills range from 0 (untrained) to 10 (master)
    - Total development points: 40
    """
    combat: Dict[str, int] = Field(
        default_factory=dict,
        description="Combat skills (melee, ranged, defense)"
    )
    general: Dict[str, int] = Field(
        default_factory=dict,
        description="General skills (athletics, perception, survival)"
    )
    stealth: Dict[str, int] = Field(
        default_factory=dict,
        description="Stealth and subterfuge (stealth, lockpicking, disguise)"
    )
    social: Dict[str, int] = Field(
        default_factory=dict,
        description="Social interaction (persuasion, intimidation, deception)"
    )
    magic: Dict[str, int] = Field(
        default_factory=dict,
        description="Magic abilities (spellcasting, ritual, enchantment)"
    )
    crafting: Dict[str, int] = Field(
        default_factory=dict,
        description="Craft and creation (smithing, alchemy, engineering)"
    )
    
    @field_validator('combat', 'general', 'stealth', 'social', 'magic', 'crafting')
    @classmethod
    def validate_skill_ranks(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Ensure all skill ranks are between 0 and 10"""
        for skill_name, rank in v.items():
            if not (0 <= rank <= 10):
                raise ValueError(f"Skill rank for {skill_name} must be between 0 and 10, got {rank}")
        return v
    
    @model_validator(mode='after')
    def validate_total_development_points(self) -> 'Skills':
        """Ensure total development points don't exceed 40"""
        total = self.get_total_development_points()
        if total > 40:
            raise ValueError(f"Total development points ({total}) exceed maximum of 40")
        return self
    
    def get_total_development_points(self) -> int:
        """Calculate total development points used"""
        total = 0
        for skill_group in [self.combat, self.general, self.stealth, 
                           self.social, self.magic, self.crafting]:
            total += sum(skill_group.values())
        return total
    
    def get_skill_rank(self, skill_name: str) -> int:
        """Get rank for a specific skill across all groups"""
        for group in [self.combat, self.general, self.stealth, 
                     self.social, self.magic, self.crafting]:
            if skill_name in group:
                return group[skill_name]
        return 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "combat": {"sword_combat": 5, "archery": 3},
                "general": {"athletics": 4, "perception": 3},
                "stealth": {"stealth": 3, "lockpicking": 2},
                "social": {"persuasion": 4, "intimidation": 2},
                "magic": {"fire_magic": 3, "healing": 2},
                "crafting": {"blacksmithing": 5, "alchemy": 4}
            }
        }
    )


class Equipment(BaseModel):
    """Simplified equipment system"""
    weapons: List[Dict] = Field(
        default_factory=list,
        description="Equipped weapons with stats"
    )
    armor: List[Dict] = Field(
        default_factory=list,
        description="Equipped armor pieces"
    )
    accessories: List[Dict] = Field(
        default_factory=list,
        description="Accessories and magical items"
    )
    consumables: List[Dict] = Field(
        default_factory=list,
        description="Consumable items (potions, scrolls)"
    )
    gold: int = Field(default=0, ge=0, description="Gold pieces")
    
    def get_total_weight(self) -> float:
        """Calculate total equipment weight"""
        total_weight = 0.0
        for item_list in [self.weapons, self.armor, self.accessories, self.consumables]:
            for item in item_list:
                total_weight += item.get('weight', 0)
        return total_weight
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "weapons": [
                    {"name": "longsword", "damage": "1d8", "weight": 5}
                ],
                "armor": [
                    {"name": "leather_armor", "defense": 2, "weight": 10}
                ],
                "accessories": [
                    {"name": "ring_of_power", "bonus": "+1 charisma"}
                ],
                "consumables": [
                    {"name": "health_potion", "quantity": 3, "effect": "heal 2d8"}
                ],
                "gold": 100
            }
        }
    )


class CombatStats(BaseModel):
    """
    Simplified combat statistics
    
    Calculation:
    - hit_points = constitution * 10 + level * 5
    - mana_points = intelligence * 5 + wisdom * 3
    - armor_class = 10 + agility_modifier + armor_bonus
    """
    max_hit_points: int = Field(..., ge=1, description="Maximum health")
    current_hit_points: int = Field(..., ge=0, description="Current health")
    max_mana_points: int = Field(default=0, ge=0, description="Maximum magical energy")
    current_mana_points: int = Field(default=0, ge=0, description="Current magical energy")
    armor_class: int = Field(default=10, ge=1, le=30, description="Defense rating")
    attack_bonus: int = Field(default=0, description="Base attack modifier")
    
    @model_validator(mode='after')
    def validate_current_stats(self) -> 'CombatStats':
        """Ensure current HP/MP don't exceed maximum"""
        if self.current_hit_points > self.max_hit_points:
            raise ValueError("Current HP cannot exceed maximum HP")
        if self.current_mana_points > self.max_mana_points:
            raise ValueError("Current MP cannot exceed maximum MP")
        return self
    
    def is_alive(self) -> bool:
        """Check if character is alive"""
        return self.current_hit_points > 0
    
    def heal(self, amount: int) -> int:
        """Heal character and return actual amount healed"""
        old_hp = self.current_hit_points
        self.current_hit_points = min(
            self.current_hit_points + amount,
            self.max_hit_points
        )
        return self.current_hit_points - old_hp
    
    def take_damage(self, amount: int) -> int:
        """Apply damage and return actual damage taken"""
        old_hp = self.current_hit_points
        self.current_hit_points = max(0, self.current_hit_points - amount)
        return old_hp - self.current_hit_points
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "max_hit_points": 50,
                "current_hit_points": 50,
                "max_mana_points": 30,
                "current_mana_points": 30,
                "armor_class": 15,
                "attack_bonus": 3
            }
        }
    )


class Spells(BaseModel):
    """
    Simplified magic system
    3 main spheres: Universal, Healer, Elemental
    """
    known_spells: List[str] = Field(
        default_factory=list,
        description="List of known spell names"
    )
    spell_slots: Dict[int, int] = Field(
        default_factory=dict,
        description="Available spell slots by level (1-9)"
    )
    spell_bonus: int = Field(default=0, description="Magic attack modifier")
    
    def can_cast_spell(self, spell_level: int) -> bool:
        """Check if character has available spell slot for given level"""
        return self.spell_slots.get(spell_level, 0) > 0
    
    def use_spell_slot(self, spell_level: int) -> bool:
        """Use a spell slot and return success status"""
        if self.can_cast_spell(spell_level):
            self.spell_slots[spell_level] -= 1
            return True
        return False
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "known_spells": ["fireball", "heal", "lightning_bolt", "shield"],
                "spell_slots": {1: 4, 2: 3, 3: 2},
                "spell_bonus": 4
            }
        }
    )


class CharacterV2(BaseModel):
    """
    Simplified character model with strict Pydantic validation
    
    All fields in English for backend consistency.
    Simplified from original system:
    - 400 stat points (down from 550)
    - 40 skill development points (down from 84)
    - 6 stat attributes (unchanged)
    - 6 skill groups (down from 9)
    """
    
    # Identity
    id: UUID = Field(default_factory=uuid4, description="Unique character identifier")
    name: str = Field(..., min_length=1, max_length=100, description="Character name")
    race: str = Field(..., min_length=1, max_length=50, description="Character race")
    culture: str = Field(..., min_length=1, max_length=50, description="Character culture")
    level: int = Field(default=1, ge=1, le=20, description="Character level")
    
    # Core stats (simplified: 400 points)
    stats: Stats = Field(..., description="Character base statistics")
    
    # Skills (simplified: 40 development points)
    skills: Skills = Field(..., description="Character trained skills")
    
    # Game mechanics
    status: CharacterStatus = Field(default=CharacterStatus.DRAFT, description="Character lifecycle status")
    experience_points: int = Field(default=0, ge=0, description="Total experience points")
    
    # Equipment and inventory
    equipment: Equipment = Field(
        default_factory=Equipment,
        description="Character equipment and inventory"
    )
    
    # Combat and magic
    combat_stats: CombatStats = Field(..., description="Combat-related statistics")
    spells: Spells = Field(
        default_factory=Spells,
        description="Known spells and magic abilities"
    )

    # Descriptions
    physical_description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Physical appearance description (height, build, features)"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Last update timestamp")
    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Character background and description"
    )
    
    def update_timestamp(self) -> None:
        """Update the last modified timestamp"""
        self.updated_at = datetime.now(timezone.utc)
    
    def level_up(self) -> None:
        """
        Level up character
        - Increase level by 1
        - Update combat stats based on new level
        """
        if self.level < 20:
            self.level += 1
            # Recalculate HP and MP based on new level
            hp_increase = 5
            self.combat_stats.max_hit_points += hp_increase
            self.combat_stats.current_hit_points += hp_increase
            self.update_timestamp()
    
    def add_experience(self, amount: int) -> bool:
        """
        Add experience points and check for level up
        Returns True if character leveled up
        """
        self.experience_points += amount
        # Simple level up threshold: 1000 XP per level
        required_xp = self.level * 1000
        if self.experience_points >= required_xp:
            self.level_up()
            return True
        return False
    
    def calculate_initiative(self) -> int:
        """Calculate combat initiative bonus"""
        agility_mod = self.stats.get_modifier('agility')
        wisdom_mod = self.stats.get_modifier('wisdom')
        return agility_mod + (wisdom_mod // 2)
    
    def get_skill_check_bonus(self, skill_name: str, stat_name: str) -> int:
        """
        Calculate total bonus for a skill check
        Total = skill rank + stat modifier
        """
        skill_rank = self.skills.get_skill_rank(skill_name)
        stat_modifier = self.stats.get_modifier(stat_name)
        return skill_rank + stat_modifier

    # --- Compatibility properties for legacy services ---
    @property
    def xp(self) -> int:
        """Compat: maps legacy xp to experience_points"""
        return self.experience_points

    @xp.setter
    def xp(self, value: int) -> None:
        self.experience_points = max(0, int(value))

    @property
    def gold(self) -> int:
        """Compat: expose gold at character root (maps to equipment.gold)"""
        return self.equipment.gold

    @gold.setter
    def gold(self, value: int) -> None:
        self.equipment.gold = max(0, int(value))

    @property
    def hp(self) -> int:
        """Compat: expose current HP at character root (maps to combat_stats.current_hit_points)"""
        return self.combat_stats.current_hit_points

    @hp.setter
    def hp(self, value: int) -> None:
        value_int = max(0, int(value))
        self.combat_stats.current_hit_points = min(value_int, self.combat_stats.max_hit_points)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Aragorn",
                "race": "Human",
                "culture": "Dúnedain",
                "level": 5,
                "stats": {
                    "strength": 16,
                    "constitution": 14,
                    "agility": 15,
                    "intelligence": 12,
                    "wisdom": 14,
                    "charisma": 16
                },
                "skills": {
                    "combat": {"sword_combat": 7, "archery": 5},
                    "general": {"athletics": 6, "perception": 5, "survival": 8},
                    "stealth": {"stealth": 4},
                    "social": {"persuasion": 5, "leadership": 6},
                    "magic": {},
                    "crafting": {"herbalism": 3}
                },
                "combat_stats": {
                    "max_hit_points": 60,
                    "current_hit_points": 60,
                    "max_mana_points": 15,
                    "current_mana_points": 15,
                    "armor_class": 17,
                    "attack_bonus": 5
                },
                "status": "active",
                "experience_points": 4500,
                "description": "A ranger of the North, heir to Isildur.",
                "physical_description": "Tall, weathered, dark-haired, with keen grey eyes."
            }
        }
    )


# Export main classes
__all__ = [
    'CharacterV2',
    'CharacterStatus',
    'Stats',
    'Skills',
    'Equipment',
    'CombatStats',
    'Spells'
]