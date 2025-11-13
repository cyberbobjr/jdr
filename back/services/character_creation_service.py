"""
Service dedicated to character creation for the role-playing game.
This service manages the automatic allocation of characteristics, rule checking,
and provides lists of races, skills, cultures, equipment, and spells.
"""

from back.models.domain.stats_manager import StatsManager
from back.models.domain.skills_manager import SkillsManager
from back.models.domain.races_manager import RacesManager
from back.models.domain.spells_manager import SpellsManager
from back.models.domain.equipment_manager import EquipmentManager
from back.models.schema import RaceData

class CharacterCreationService:
    """
    Service for managing character creation.
    """

    @staticmethod
    def allocate_attributes_auto(race_data: RaceData) -> dict:
        """
        ### allocate_attributes_auto
        **Description:** Automatically allocates a character's attributes according to their race, optimizing the distribution according to business recommendations and integrating racial bonuses into the budget calculation, without an infinite loop.
        **Parameters:**
        - `race_data` (RaceData): The character's complete race object.
        **Returns:** A dictionary of allocated attributes.
        """
        stats_manager = StatsManager()
        # Get the names of the characteristics and the budget
        char_names = list(stats_manager.get_all_stats_names())
        starting_points = stats_manager.starting_points
        
        # Racial bonuses to be integrated into the distribution
        racial_bonuses = race_data.characteristic_bonuses if race_data else {}
        
        # 1. Start from a minimum base (50 everywhere)
        values = {name: 50 for name in char_names}
        # 2. To simplify, we distribute the remaining budget equally
        remaining_budget = starting_points - sum(values.values())
        
        # 3. Equal distribution
        while remaining_budget > 0 and any(values[name] < 70 for name in char_names):
            improved = False
            for char_name in char_names:
                if remaining_budget > 0 and values[char_name] < 70:
                    values[char_name] += 1
                    remaining_budget -= 1
                    improved = True
            if not improved:
                break
        
        # 4. Apply racial bonuses for the final result
        for char_name in char_names:
            if char_name in racial_bonuses:
                values[char_name] += racial_bonuses[char_name]
        
        return values

    @staticmethod
    def check_attributes_points(attributes: dict) -> bool:
        """
        ### check_attributes_points
        **Description:** Checks that the attribute points respect the creation rules (budget, limits, etc.).
        **Parameters:**
        - `attributes` (dict): Dictionary of the character's attributes.
        **Returns:** A boolean indicating if the points are valid.
        """
        stats_manager = StatsManager()
        
        # Check the total budget
        total_cost = 0
        for value in attributes.values():
            total_cost += stats_manager.calculate_cost(value)

        if total_cost > stats_manager.starting_points:
            return False
        # Check the bounds (1-100)
        for v in attributes.values():
            if v < 1 or v > 100:
                return False
        return True
    
    @staticmethod
    def get_races() -> list:
        """
        ### get_races
        **Description:** Returns the complete list of available races with all their information (cultures, bonuses, etc.).
        **Parameters:**
        - None
        **Returns:** A list of RaceData objects (complete structure from JSON).
        """
        races_manager = RacesManager()
        return races_manager.get_all_races_data()

    @staticmethod
    def get_skills() -> dict:
        """
        ### get_skills
        **Description:** Returns the complete structure of the skills_for_llm.json file (groups, skills, difficulty levels, etc.) for Swagger and frontend documentation.
        **Parameters:**
        - None
        **Returns:** A detailed dictionary conforming to skills_for_llm.json.
        """
        skills_manager = SkillsManager()
        return skills_manager.skills_data

    @staticmethod
    def check_skills_points(skills: dict) -> bool:
        """
        ### check_skills_points
        **Description:** Checks the validity of the distribution of skill points.
        **Parameters:**
        - `skills` (dict): Dictionary of skills and attributed points.
        **Returns:** True if the distribution is valid, False otherwise.
        """
        # Simple logic: each skill must be between 0 and 6, total max 40
        if not isinstance(skills, dict):
            return False
        total = 0
        for v in skills.values():
            if not (0 <= v <= 6):
                return False
            total += v
        return total <= 40

    @staticmethod
    def calculate_skills_cost(skills: dict) -> int:
        """
        ### calculate_skills_cost
        **Description:** Calculates the total cost of the skill distribution.
        **Parameters:**
        - `skills` (dict): Dictionary of skills and attributed points.
        **Returns:** The total cost (int).
        """
        if not isinstance(skills, dict):
            return 0
        return sum(skills.values())

    @staticmethod
    def get_equipments() -> list:
        """
        ### get_equipments
        **Description:** Returns the list of available equipment.
        **Parameters:**
        - None
        **Returns:** A list of equipment (str).
        """
        equipment_manager = EquipmentManager()
        return equipment_manager.get_equipment_names()

    @staticmethod
    def get_spells() -> list:
        """
        ### get_spells
        **Description:** Returns the list of available spells.
        **Parameters:**
        - None
        **Returns:** A list of spells (str).
        """
        spells_manager = SpellsManager()
        all_spells = []
        for spell_data in spells_manager.get_all_spells():
            all_spells.append(spell_data["name"])
        return all_spells