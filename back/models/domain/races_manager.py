import json
import os
from typing import Dict, List, Any, Optional
from ...config import get_data_dir
from ..schema import RaceData, CultureData

class RacesManager:
    """Manages races and cultures using the new simplified JSON system"""

    def __init__(self):
        self._load_races_data()

    def _load_races_data(self):
        """Loads data from the JSON file"""
        data_path = os.path.join(get_data_dir(), "races_and_cultures.json")
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                self.races_data = [RaceData(**race) for race in json.load(f)]
        except FileNotFoundError:
            # Fallback to minimal data
            self.races_data = [
                RaceData(
                    id="humans",
                    name="Humans",
                    characteristic_bonuses={"Willpower": 1},
                    base_languages=["Westron"],
                    optional_languages=[],
                    cultures=[]
                )
            ]

    def get_all_races(self) -> List[RaceData]:
        """Returns the complete list of races"""
        return self.races_data

    def get_race_by_id(self, race_id: str) -> Optional[RaceData]:
        """Returns data for a race by its id"""
        for race in self.races_data:
            if race.id == race_id:
                return race
        return None

    def get_race_by_name(self, race_name: str) -> Optional[RaceData]:
        """Returns data for a race by its name"""
        for race in self.races_data:
            if race.name == race_name:
                return race
        return None

    def get_cultures_for_race(self, race_id: str) -> List[CultureData]:
        """Returns the available cultures for a race"""
        race = self.get_race_by_id(race_id)
        if race:
            return race.cultures or []
        return []

    def get_culture_by_id(self, race_id: str, culture_id: str) -> Optional[CultureData]:
        """Returns data for a specific culture"""
        cultures = self.get_cultures_for_race(race_id)
        for culture in cultures:
            if culture.id == culture_id:
                return culture
        return None

    def get_characteristic_bonuses(self, race_id: str, culture_id: str = None) -> Dict[str, int]:
        """Returns all characteristic bonuses (race + culture)"""
        bonuses = {}

        # Racial bonuses
        race = self.get_race_by_id(race_id)
        if race:
            bonuses.update(race.characteristic_bonuses or {})

        # Cultural bonuses (if specified)
        if culture_id:
            culture = self.get_culture_by_id(race_id, culture_id)
            if culture:
                bonuses.update(culture.characteristic_bonuses or {})

        return bonuses

    def get_skill_bonuses(self, race_id: str, culture_id: str) -> Dict[str, int]:
        """Returns the skill bonuses of a culture"""
        culture = self.get_culture_by_id(race_id, culture_id)
        if culture:
            return culture.skill_bonuses or {}
        return {}

    def get_languages(self, race_id: str) -> Dict[str, List[str]]:
        """Returns the base and optional languages of a race"""
        race = self.get_race_by_id(race_id)
        if race:
            return {
                "base": race.base_languages or [],
                "optional": race.optional_languages or []
            }
        return {"base": [], "optional": []}

    def get_free_skill_points(self, race_id: str, culture_id: str) -> int:
        """Returns the number of free skill points"""
        culture = self.get_culture_by_id(race_id, culture_id)
        if culture:
            return culture.free_skill_points or 0
        return 0

    def get_special_traits(self, race_id: str, culture_id: str) -> Dict[str, Any]:
        """Returns the special traits of a culture"""
        culture = self.get_culture_by_id(race_id, culture_id)
        if culture:
            return culture.special_traits or {}
        return {}

    def get_culture_description(self, race_id: str, culture_id: str) -> str:
        """Returns the description/traits of a culture"""
        culture = self.get_culture_by_id(race_id, culture_id)
        if culture:
            return culture.traits or ""
        return ""

    def get_complete_character_bonuses(self, race_id: str, culture_id: str) -> Dict[str, Any]:
        """Returns all bonuses and traits for a character (race + culture)"""
        return {
            "characteristic_bonuses": self.get_characteristic_bonuses(race_id, culture_id),
            "skill_bonuses": self.get_skill_bonuses(race_id, culture_id),
            "languages": self.get_languages(race_id),
            "free_skill_points": self.get_free_skill_points(race_id, culture_id),
            "special_traits": self.get_special_traits(race_id, culture_id),
            "culture_description": self.get_culture_description(race_id, culture_id)
        }

    def get_all_races_data(self) -> List[RaceData]:
        """Returns the complete list of race data (not just names)"""
        return self.races_data

    def get_race_names(self) -> List[str]:
        """Returns only the names of the races"""
        return [race.name for race in self.races_data]
