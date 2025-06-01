from typing import Optional, List, Dict
from .base import Race

# Ajout d'une propriété stat_bonuses pour compatibilité
if not hasattr(Race, "stat_bonuses"):
    @property
    def stat_bonuses(self):
        return self.characteristic_bonuses
    Race.stat_bonuses = stat_bonuses

class Races:
    """Gestion des races et sous-cultures"""
    
    def __init__(self):
        self.RACES_DATA = self._load_races_data()
    
    def _load_races_data(self) -> Dict[str, Race]:
        return {
            "Homme": Race(
                name="Homme",
                sub_cultures=["Sylvestre", "Nomade", "Rurale", "Citadine", "Sous-Collines", "Grottes"],
                characteristic_bonuses={},  # 8 points à répartir
                endurance_bonus=30, pp_bonus=30,
                body_resistance=10, mind_resistance=10, magic_resistance=10,
                special_abilities=["Apprenti Doué", "Enfant Prodige", "Faculté d'Adaptation", "Focalisation Adolescente"]
            ),
            "Númenóréen": Race(
                name="Númenóréen",
                sub_cultures=["Sylvestre", "Rurale", "Citadine"],
                characteristic_bonuses={"Force": 2, "Constitution": 2, "Volonté": 3, "Raisonnement": 3, "Présence": 3},
                endurance_bonus=40, pp_bonus=35,
                body_resistance=15, mind_resistance=15, magic_resistance=15,
                special_abilities=["Longue Vie"]
            ),
            "Elfe Noldo": Race(
                name="Elfe Noldo",
                sub_cultures=["Noldo", "Sylvestre", "Citadine"],
                characteristic_bonuses={"Force": 2, "Constitution": 3, "Agilité": 3, "Rapidité": 3, "Volonté": 2, "Raisonnement": 2, "Intuition": 2, "Présence": 5},
                endurance_bonus=30, pp_bonus=40,
                body_resistance=15, mind_resistance=15, magic_resistance=20,
                special_abilities=["Immortalité", "Expérimenté", "Cicatrisation Parfaite", "Pas Léger des Elfes", "Résistance à la Fatigue", "Résistance aux Intempéries", "Résistance aux Maladies", "Transe Elfique", "Vision Elfique"]
            ),
            "Elfe Sinda": Race(
                name="Elfe Sinda",
                sub_cultures=["Sinda", "Sylvestre", "Rurale", "Citadine"],
                characteristic_bonuses={"Force": 1, "Constitution": 3, "Agilité": 2, "Rapidité": 3, "Volonté": 3, "Intuition": 5},
                endurance_bonus=30, pp_bonus=40,
                body_resistance=15, mind_resistance=15, magic_resistance=20,
                special_abilities=["Immortalité", "Expérimenté", "Cicatrisation Parfaite", "Pas Léger des Elfes", "Résistance à la Fatigue", "Résistance aux Intempéries", "Résistance aux Maladies", "Transe Elfique", "Vision Elfique"]
            ),
            "Elfe Sylvain": Race(
                name="Elfe Sylvain",
                sub_cultures=["Sylvain", "Sylvestre", "Rurale"],
                characteristic_bonuses={"Agilité": 4, "Rapidité": 4, "Volonté": 2},
                endurance_bonus=40, pp_bonus=30,
                body_resistance=15, mind_resistance=15, magic_resistance=20,
                special_abilities=["Immortalité", "Expérimenté", "Cicatrisation Parfaite", "Pas Léger des Elfes", "Résistance à la Fatigue", "Résistance aux Intempéries", "Résistance aux Maladies", "Transe Elfique", "Vision Elfique"]
            ),
            "Hobbit": Race(
                name="Hobbit",
                sub_cultures=["Hobbit", "Sous-Collines", "Rurale", "Citadine"],
                characteristic_bonuses={"Force": -2, "Constitution": 3, "Agilité": 4, "Rapidité": 3, "Volonté": 2, "Présence": -1},
                endurance_bonus=35, pp_bonus=0,
                body_resistance=15, mind_resistance=15, magic_resistance=15,
                special_abilities=["Résistance à la Fatigue", "Résistance aux Intempéries", "Six Repas par Jour"]
            ),
            "Nain": Race(
                name="Nain",
                sub_cultures=["Nain", "Cavernes Profondes", "Grottes", "Citadine"],
                characteristic_bonuses={"Force": 4, "Constitution": 4, "Volonté": 3, "Présence": -1},
                endurance_bonus=50, pp_bonus=10,
                body_resistance=15, mind_resistance=10, magic_resistance=15,
                special_abilities=["Nager Comme un Nain", "Né de la Pierre", "Résistance à la Fatigue", "Résistance aux Intempéries"]
            )
        }
    
    def get_race(self, race_name: str) -> Optional[Race]:
        return self.RACES_DATA.get(race_name)
    
    def get_available_races(self) -> List[str]:
        return list(self.RACES_DATA.keys())

    def get_all_races(self) -> List[str]:
        # Alias pour compatibilité avec character_creation_graph.py
        return self.get_available_races()

    def calculate_stat_bonus(self, value: int) -> int:
        """Calcule le bonus de caractéristique à partir de la valeur brute."""
        # Exemple de règle : (valeur - 50) // 5
        return (value - 50) // 5
