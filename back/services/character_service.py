# Unitary Business Logic (SRP)

from typing import List, Dict, Optional
from back.models.schema import CharacterStatus
from back.models.domain.character import Character
from back.utils.logger import log_debug, log_info, log_warning, get_logger
from back.utils.model_converter import ModelConverter
from back.services.character_data_service import CharacterDataService

logger = get_logger(__name__)

class CharacterService:
    """
    ### CharacterService
    **Description:** Service responsible for character-related business logic.
    It acts as an abstraction layer above `CharacterDataService` for operations
    that modify the character's state (XP, Gold, HP, Rest).
    
    **Usage:**
    This service is used by `GameSessionService` to expose business methods to Tools
    and agents. It is not meant to be instantiated directly by controllers, but rather
    via `GameSessionService` which manages the session context.

    **Attributes:**
    - `character_id` (str): The unique identifier of the managed character.
    - `strict_validation` (bool): Indicates if strict data validation is enabled.
    - `data_service` (CharacterDataService): Data access service (persistence).
    - `character_data` (Character): The character model object loaded in memory.
    """
    character_id: str
    strict_validation: bool
    character_data: Character
    data_service: CharacterDataService
    
    def __init__(self, character_id: str, strict_validation: bool = True) -> None:
        """
        ### __init__
        **Description:** Initializes the character service for a specific character.
        Automatically loads character data upon initialization.

        **Parameters:**
        - `character_id` (str): Identifier of the character to manage.
        - `strict_validation` (bool): If True, strictly validates with the Character model. If False, accepts incomplete characters.
        
        **Returns:** None.
        """
        self.character_id = character_id
        self.strict_validation = strict_validation
        self.data_service = CharacterDataService()
        self.character_data = self._load_character()
        
    def _load_character(self) -> Character:
        """
        ### _load_character
        **Description:** Loads character data from persistent storage via `CharacterDataService`.
        
        **Returns:** 
        - `Character`: The loaded character object.
        """
        character: Character = self.data_service.load_character(self.character_id)

        # Check if the character is complete
        is_incomplete = (
            character.name is None or
            character.status == CharacterStatus.IN_PROGRESS or
            character.status is None
        )

        log_debug("Loading character", action="_load_character", character_id=self.character_id, is_incomplete=is_incomplete)

        return character

    def save_character(self) -> None:
        """
        ### save_character
        **Description:** Saves the current character state (`self.character_data`) to persistent storage.
        This method must be called after any modification of the character's state.
        
        **Returns:** None.
        """
        self.data_service.save_character(self.character_data, self.character_id)
        log_debug("Saving character", action="save_character", character_id=self.character_id)
    
    def get_character(self) -> Character:
        """
        ### get_character
        **Description:** Returns the Character object currently loaded in memory.
        
        **Returns:** 
        - `Character`: The character object.
        """
        return self.character_data
    
    def get_character_json(self) -> str:
        """
        ### get_character_json
        **Description:** Returns character data as a JSON string.
        Useful for display or debugging.
        
        **Returns:** 
        - `str`: JSON representation of the character.
        """
        return ModelConverter.to_json(self.character_data)
    
    # --- Business Logic Methods ---

    def apply_xp(self, xp: int) -> Character:
        """
        ### apply_xp
        **Description:** Adds experience points (XP) to the character and checks if they should level up.
        
        **Parameters:**
        - `xp` (int): The amount of XP to add. Must be positive.
        
        **Returns:** 
        - `Character`: The updated character object.
        """
        if xp < 0:
            log_warning("Attempt to add negative XP", action="apply_xp", character_id=self.character_id, xp=xp)
            return self.character_data

        self.character_data.xp += xp
        
        # Check for level up (simplified logic: 1000 XP per level for example)
        # TODO: Implement a real XP table if necessary
        xp_threshold = self.character_data.level * 1000
        if self.character_data.xp >= xp_threshold:
            self.level_up()

        self.save_character()
        
        log_info("XP added to character",
                   extra={"action": "apply_xp",
                          "character_id": str(self.character_data.id),
                          "xp_added": xp,
                          "xp_total": self.character_data.xp,
                          "level": self.character_data.level})
        
        return self.character_data
    
    def level_up(self) -> None:
        """
        ### level_up
        **Description:** Handles the character's level up.
        Increases level, recalculates max HP, and heals the character.
        
        **Returns:** None.
        """
        self.character_data.level += 1
        
        # Recalculate max HP (Constitution * 10 + Level * 5)
        new_max_hp = self.calculate_max_hp()
        self.character_data.combat_stats.max_hit_points = new_max_hp
        
        # Fully heal upon leveling up
        self.character_data.combat_stats.current_hit_points = new_max_hp
        
        log_info("Level up!", 
                 extra={"action": "level_up", 
                        "character_id": str(self.character_data.id), 
                        "new_level": self.character_data.level,
                        "new_max_hp": new_max_hp})

    def add_gold(self, gold: float) -> Character:
        """
        ### add_gold
        **Description:** Adds (or removes if negative) gold to the character's wallet.
        
        **Parameters:**
        - `gold` (float): Amount of gold to add.
        
        **Returns:** 
        - `Character`: The updated character object.
        """
        self.character_data.gold += int(gold)
        # Prevent negative gold
        if self.character_data.gold < 0:
            self.character_data.gold = 0
            
        self.save_character()
        
        log_info("Gold modified for character",
                   extra={"action": "add_gold",
                          "character_id": str(self.character_data.id),
                          "gold_added": gold,
                          "gold_total": self.character_data.gold})
        
        return self.character_data
    
    def take_damage(self, amount: int, source: str = "combat") -> Character:
        """
        ### take_damage
        **Description:** Applies damage to the character by reducing their current hit points.
        Delegates logic to `combat_stats.take_damage`.
        
        **Parameters:**
        - `amount` (int): Damage points to apply.
        - `source` (str): The source of damage (e.g., "combat", "trap", "fall").
        
        **Returns:** 
        - `Character`: The updated character object.
        """
        # Delegate to combat stats to ensure consistency
        self.character_data.combat_stats.take_damage(int(amount))
        self.save_character()
        
        log_warning("Damage applied to character",
                       extra={"action": "take_damage",
                              "character_id": str(self.character_data.id),
                              "amount": amount,
                              "hp_remaining": self.character_data.hp,
                              "source": source})
        
        return self.character_data
    
    def heal(self, amount: int, source: str = "heal") -> Character:
        """
        ### heal
        **Description:** Restores hit points to the character.
        Cannot exceed maximum HP.
        
        **Parameters:**
        - `amount` (int): Hit points to restore.
        - `source` (str): The source of healing (e.g., "potion", "spell", "rest").
        
        **Returns:** 
        - `Character`: The updated character object.
        """
        max_hp = self.character_data.combat_stats.max_hit_points
        current_hp = self.character_data.hp
        
        new_hp = min(max_hp, current_hp + int(amount))
        self.character_data.hp = new_hp
        
        self.save_character()
        
        log_info("Healing applied to character",
                   extra={"action": "heal",
                          "character_id": str(self.character_data.id),
                          "amount": amount,
                          "hp_remaining": self.character_data.hp,
                          "source": source})
        
        return self.character_data

    def calculate_max_hp(self) -> int:
        """
        ### calculate_max_hp
        **Description:** Calculates the character's theoretical max HP based on their stats.
        Formula: Constitution * 10 + Level * 5.
        
        **Returns:** 
        - `int`: Calculated max HP.
        """
        constitution = self.character_data.stats.constitution
        level = self.character_data.level
        return constitution * 10 + level * 5
    
    def is_alive(self) -> bool:
        """
        ### is_alive
        **Description:** Checks if the character is still alive (HP > 0).
        
        **Returns:** 
        - `bool`: True if alive, False if dead.
        """
        return self.character_data.combat_stats.is_alive()
    
    def short_rest(self) -> Character:
        """
        ### short_rest
        **Description:** Performs a short rest.
        House rule: Restores 25% of maximum HP.
        
        **Returns:** 
        - `Character`: The updated character object.
        """
        max_hp = self.character_data.combat_stats.max_hit_points
        heal_amount = int(max_hp * 0.25)
        
        log_info("Short rest performed", action="short_rest", character_id=self.character_id, heal_amount=heal_amount)
        return self.heal(heal_amount, source="short_rest")

    def long_rest(self) -> Character:
        """
        ### long_rest
        **Description:** Performs a long rest.
        Restores all HP and (potentially) other resources (Mana, etc.).
        
        **Returns:** 
        - `Character`: The updated character object.
        """
        max_hp = self.character_data.combat_stats.max_hit_points
        missing_hp = max_hp - self.character_data.hp
        
        # Restore Mana if applicable (logic to be extended as needed)
        if hasattr(self.character_data.combat_stats, 'max_mana_points'):
             self.character_data.combat_stats.current_mana_points = self.character_data.combat_stats.max_mana_points

        log_info("Long rest performed", action="long_rest", character_id=self.character_id, heal_amount=missing_hp)
        return self.heal(missing_hp, source="long_rest")
