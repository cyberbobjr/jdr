import json
from typing import Dict, List, Any, Optional
from pathlib import Path

class RacesManager:
    """Gestionnaire des races et cultures utilisant le nouveau système JSON simplifié"""
    
    def __init__(self):
        self._load_races_data()
    
    def _load_races_data(self):
        """Charge les données depuis le fichier JSON"""
        data_path = Path(__file__).parent.parent.parent.parent / "data" / "races_and_cultures.json"
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                self.races_data = json.load(f)
        except FileNotFoundError:
            # Fallback vers des données minimales
            self.races_data = [
                {
                    "name": "Humains",
                    "characteristic_bonuses": {"Volonté": 1},
                    "destiny_points": 3,
                    "base_languages": ["Ouistrain"],
                    "optional_languages": [],
                    "cultures": []
                }
            ]

    def get_all_races(self) -> List[str]:
        """Retourne la liste de toutes les races disponibles"""
        return [race["name"] for race in self.races_data]

    def get_race_by_name(self, race_name: str) -> Optional[Dict]:
        """Retourne les données d'une race par son nom"""
        for race in self.races_data:
            if race["name"] == race_name:
                return race
        return None

    def get_cultures_for_race(self, race_name: str) -> List[Dict]:
        """Retourne les cultures disponibles pour une race"""
        race = self.get_race_by_name(race_name)
        if race:
            return race.get("cultures", [])
        return []

    def get_culture_by_name(self, race_name: str, culture_name: str) -> Optional[Dict]:
        """Retourne les données d'une culture spécifique"""
        cultures = self.get_cultures_for_race(race_name)
        for culture in cultures:
            if culture["name"] == culture_name:
                return culture
        return None

    def get_characteristic_bonuses(self, race_name: str, culture_name: str = None) -> Dict[str, int]:
        """Retourne tous les bonus de caractéristiques (race + culture)"""
        bonuses = {}
        
        # Bonus raciaux
        race = self.get_race_by_name(race_name)
        if race:
            bonuses.update(race.get("characteristic_bonuses", {}))
        
        # Bonus culturels (si spécifiés)
        if culture_name:
            culture = self.get_culture_by_name(race_name, culture_name)
            if culture:
                bonuses.update(culture.get("characteristic_bonuses", {}))
        
        return bonuses

    def get_skill_bonuses(self, race_name: str, culture_name: str) -> Dict[str, int]:
        """Retourne les bonus de compétences d'une culture"""
        culture = self.get_culture_by_name(race_name, culture_name)
        if culture:
            return culture.get("skill_bonuses", {})
        return {}

    def get_destiny_points(self, race_name: str, culture_name: str = None) -> int:
        """Retourne le nombre de points de destin"""
        race = self.get_race_by_name(race_name)
        base_points = race.get("destiny_points", 2) if race else 2
        
        # Vérifier si la culture donne des points de destin bonus
        if culture_name:
            culture = self.get_culture_by_name(race_name, culture_name)
            if culture and "special_traits" in culture:
                bonus = culture["special_traits"].get("bonus_destiny_points", 0)
                base_points += bonus
        
        return base_points

    def get_languages(self, race_name: str) -> Dict[str, List[str]]:
        """Retourne les langues de base et optionnelles d'une race"""
        race = self.get_race_by_name(race_name)
        if race:
            return {
                "base": race.get("base_languages", []),
                "optional": race.get("optional_languages", [])
            }
        return {"base": [], "optional": []}

    def get_free_skill_points(self, race_name: str, culture_name: str) -> int:
        """Retourne le nombre de points de compétence libres"""
        culture = self.get_culture_by_name(race_name, culture_name)
        if culture:
            return culture.get("free_skill_points", 0)
        return 0

    def get_special_traits(self, race_name: str, culture_name: str) -> Dict[str, Any]:
        """Retourne les traits spéciaux d'une culture"""
        culture = self.get_culture_by_name(race_name, culture_name)
        if culture:
            return culture.get("special_traits", {})
        return {}

    def get_culture_description(self, race_name: str, culture_name: str) -> str:
        """Retourne la description/traits d'une culture"""
        culture = self.get_culture_by_name(race_name, culture_name)
        if culture:
            return culture.get("traits", "")
        return ""

    def get_complete_character_bonuses(self, race_name: str, culture_name: str) -> Dict[str, Any]:
        """Retourne tous les bonus et traits pour un personnage (race + culture)"""
        return {
            "characteristic_bonuses": self.get_characteristic_bonuses(race_name, culture_name),
            "skill_bonuses": self.get_skill_bonuses(race_name, culture_name),
            "destiny_points": self.get_destiny_points(race_name, culture_name),
            "languages": self.get_languages(race_name),
            "free_skill_points": self.get_free_skill_points(race_name, culture_name),
            "special_traits": self.get_special_traits(race_name, culture_name),
            "culture_description": self.get_culture_description(race_name, culture_name)
        }

    def get_all_races_data(self) -> List[Dict]:
        """Retourne la liste complète des données de races (pas seulement les noms)"""
        return self.races_data

    def get_race_names(self) -> List[str]:
        """Retourne uniquement les noms des races"""
        return [race["name"] for race in self.races_data]
