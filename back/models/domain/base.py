from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from back.config import get_data_dir
import json

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
class Profession:
    name: str
    description: str
    favored_skill_groups: Dict[str, int]
    main_characteristics: List[str]
    abilities: List[str]
    spheres: List[str]

    @classmethod
    def load_all_from_json(cls) -> List["Profession"]:
        """
        ### load_all_from_json
        **Description:** Charge la liste des professions depuis le fichier JSON centralisé et retourne des instances de Profession.
        **Parameters:**
        - Aucun
        **Returns:** Liste d'instances Profession.
        """
        import os
        data_path = os.path.join(get_data_dir(), 'professions.json')
        with open(data_path, encoding='utf-8') as f:
            data = json.load(f)
        return [cls(**p) for p in data]

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

@dataclass
class CultureData:
    name: str
    bonus: str
    traits: str

@dataclass
class RaceData:
    name: str
    characteristic_bonuses: Dict[str, int]
    destiny_points: int
    special_abilities: List[str]
    base_languages: List[str]
    optional_languages: List[str]
    cultures: List[CultureData]
