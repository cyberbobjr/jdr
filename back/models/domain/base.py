from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

class Difficulty(Enum):
    ROUTINE = 60
    VERY_EASY = 40
    EASY = 20
    AVERAGE = 0
    HARD = -20
    VERY_HARD = -40
    EXTREMELY_HARD = -60
    SHEER_FOLLY = -80
    ABSURD = -100

@dataclass
class CharacteristicBonus:
    value: int
    bonus: int

@dataclass
class Race:
    name: str
    sub_cultures: List[str]
    characteristic_bonuses: Dict[str, int]
    endurance_bonus: int
    pp_bonus: int
    body_resistance: int
    mind_resistance: int
    magic_resistance: int
    special_abilities: List[str]

@dataclass
class Profession:
    name: str
    description: str
    favored_skill_groups: Dict[str, int]
    main_characteristics: List[str]
    abilities: List[str]
    spheres: List[str]

@dataclass
class Culture:
    name: str
    description: str
    adolescence_skills: Dict[str, int]

@dataclass
class Skill:
    name: str
    group: str
    characteristics: Tuple[str, str]
    resolution_type: str
    description: str
    special_rules: Optional[str] = None

@dataclass
class Equipment:
    name: str
    price: int  # en pièces de cuivre
    weight: float  # en kg
    category: str
    description: Optional[str] = None

@dataclass
class Spell:
    name: str
    sphere: str
    description: str
    duration: str
    cost: int  # en PP
    range: str
    resistance: str
    level: int  # Niveau du sort ajouté ici
    bonus: Optional[str] = None
    malus: Optional[str] = None
    dice_rolls: Optional[str] = None
