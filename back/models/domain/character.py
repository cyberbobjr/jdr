from typing import Dict, List, Optional
from pydantic import BaseModel
from uuid import UUID

from back.models.domain.stats_manager import StatsManager
from back.models.schema import Item, RaceData, CultureData, CharacterStatus

class Character(BaseModel):
    """
    ### Character
    **Description:** Data model representing a player or non-player character in the RPG. Uses the correct definition from the main schema.
    **Attributes:**
    - `id` (UUID): Unique identifier for the character.
    - `name` (str): The character's name.
    - `race` (RaceData): Complete race object with all bonuses and details.
    - `culture` (CultureData): Complete culture object with all bonuses and details.
    - `stats` (Dict[str, int]): Main characteristics (Strength, Constitution, etc.).
    - `skills` (Dict[str, int]): Skills and their levels.
    - `hp` (int): Hit points (calculated from Constitution).
    - `xp` (int): Experience points.
    - `gold` (float): Gold owned (can have decimals).
    - `inventory` (List[Item]): Detailed inventory with complete items.
    - `spells` (List[str]): List of known spells.
    - `culture_bonuses` (Dict[str, int]): Bonuses related to culture.
    - `background` (str): The character's story (narrative background).
    - `physical_description` (str): The character's physical description.
    - `status` (CharacterStatus): The character's status.
    """
    id: UUID
    name: str
    race: RaceData
    culture: CultureData
    stats: Dict[str, int]
    skills: Dict[str, int]
    hp: int = 100  # Calculated from Constitution
    xp: int = 0  # Experience points
    gold: float = 0.0  # Gold owned (can have decimals)
    inventory: List[Item] = []  # Detailed inventory with complete items
    spells: List[str] = []
    culture_bonuses: Dict[str, int]
    background: str = None  # Character's story
    physical_description: str = None  # Physical description
    status: CharacterStatus = None  # Character's status
    last_update: Optional[str] = None  # Date of last update
    
    @staticmethod
    def is_character_finalized(character_dict: Dict) -> bool:
        """
        ### is_character_finalized
        **Description:** Checks if a character passed as a dictionary contains all the mandatory fields to be considered finalized.
        **Parameters:**
        - `character_dict` (Dict): Dictionary representing a character.
        **Returns:** bool - True if the character is finalized, False otherwise.
        """
        required_fields = [
            'id', 
            'name',
            'race',
            'culture', 
            'stats', 
            'skills',
            'culture_bonuses'
        ]
        
        # Check that all required fields are present and not None
        for field in required_fields:
            if field not in character_dict or character_dict[field] is None:
                return False
        
        # Specific checks for certain fields
        # Race must have a name
        if 'name' not in character_dict.get('race', {}) or not character_dict['race']['name']:
            return False
            
        # Culture must have a name
        if 'name' not in character_dict.get('culture', {}) or not character_dict['culture']['name']:
            return False
        
        manager = StatsManager()
        stats = character_dict.get('stats', {})
        for stat in manager.get_all_stats_names():
            if stat not in stats:
                return False
                
        # Skills cannot be empty
        if not character_dict.get('skills', {}):
            return False
            
        return True