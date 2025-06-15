from typing import List
from .base import RaceData, CultureData
import json
from typing import List
from back.config import get_data_dir
import os

class Races:
    """Gestion des races et cultures (nouvelle version JSON)"""
    
    def __init__(self):
        self.RACES_DATA = self._load_races_data()

    def _load_races_data(self) -> List[RaceData]:
        """
        Charge et retourne la liste des races depuis le JSON races_and_cultures.json.
        **Returns :**
        - (List[RaceData]) : Liste des races chargées depuis le fichier JSON.
        """
        json_path = os.path.join(get_data_dir(), 'races_and_cultures.json')
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)
        races = []
        for race in data:
            cultures = [CultureData(**c) for c in race.get('cultures', [])]
            races.append(RaceData(
                name=race['name'],
                characteristic_bonuses=race['characteristic_bonuses'],
                destiny_points=race['destiny_points'],
                special_abilities=race['special_abilities'],
                base_languages=race['base_languages'],
                optional_languages=race['optional_languages'],
                cultures=cultures
            ))
        return races
    
    def get_available_races(self) -> List[str]:
        return list(self.RACES_DATA.keys())

    def get_all_races(self) -> List[str]:
        # Alias pour compatibilité avec character_creation_graph.py
        return self.get_available_races()

    def calculate_stat_bonus(self, value: int) -> int:
        """Calcule le bonus de caractéristique à partir de la valeur brute."""
        # Exemple de règle : (valeur - 50) // 5
        return (value - 50) // 5
