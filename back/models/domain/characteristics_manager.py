import json
from typing import Dict
from pathlib import Path

class CharacteristicsManager:
    """Gestionnaire des caractéristiques utilisant le nouveau système JSON"""
    
    def __init__(self):
        self.values = {}
        self.racial_bonuses = {}
        self._load_characteristics_data()
        # Initialiser les valeurs par défaut
        for name in self.names:
            self.values[name] = 50
            self.racial_bonuses[name] = 0
    
    def _load_characteristics_data(self):
        """Charge les données depuis le fichier JSON"""
        data_path = Path(__file__).parent.parent.parent.parent / "data" / "characteristics.json"
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.characteristics_info = data["characteristics"]
            self.names = list(self.characteristics_info.keys())
            self.bonus_table = data["bonus_table"]
            self.cost_table = data["cost_table"]
            self.starting_points = data["starting_points"]
            
        except FileNotFoundError:
            # Fallback vers les anciennes valeurs si le fichier n'existe pas
            self._load_fallback_data()
    
    def _load_fallback_data(self):
        """Données de fallback si le fichier JSON n'est pas trouvé"""
        self.characteristics_info = {
            "Force": {"description": "Force physique, carrure"},
            "Constitution": {"description": "Santé, résistance, vigueur"},
            "Agilité": {"description": "Dextérité manuelle, souplesse"}, 
            "Rapidité": {"description": "Réflexes, vitesse de réaction"},
            "Volonté": {"description": "Détermination, résistance mentale"},
            "Raisonnement": {"description": "Pensée logique, intelligence"},
            "Intuition": {"description": "Intuition, perception"},
            "Présence": {"description": "Charisme, leadership"}
        }
        self.names = list(self.characteristics_info.keys())
        self.bonus_table = {
            "1-5": -18, "6-10": -16, "11-15": -14, "16-20": -12,
            "21-25": -10, "26-30": -8, "31-35": -6, "36-40": -4,
            "41-45": -2, "46-50": 0, "51-55": 1, "56-60": 2,
            "61-65": 3, "66-70": 4, "71-75": 5, "76-80": 6,
            "81-85": 7, "86-90": 8, "91-95": 9, "96-100": 10,
            "101": 11, "102": 12, "103": 13, "104": 14, "105": 15
        }
        self.cost_table = {"1-90": 1, "91-95": 2, "96-100": 3, "101-105": 10}
        self.starting_points = 550

    def get_description(self, characteristic: str) -> str:
        """Retourne la description d'une caractéristique"""
        char_info = self.characteristics_info.get(characteristic, {})
        return char_info.get("description", "")

    def get_bonus(self, characteristic: str) -> int:
        """Calcule le bonus final d'une caractéristique (valeur + bonus racial)"""
        base_value = self.values.get(characteristic, 50)
        base_bonus = self._get_base_bonus(base_value)
        racial_bonus = self.racial_bonuses.get(characteristic, 0)
        return base_bonus + racial_bonus

    def _get_base_bonus(self, value: int) -> int:
        """Récupère le bonus de base selon la table"""
        # Cas spéciaux pour les valeurs exactes
        if str(value) in self.bonus_table:
            return self.bonus_table[str(value)]
          # Recherche dans les plages
        for range_key, bonus in self.bonus_table.items():
            if "-" in range_key:
                start, end = map(int, range_key.split("-"))
                if start <= value <= end:
                    return bonus
        return 0

    def calculate_cost(self, values: Dict[str, int]) -> int:
        """Calcule le coût total des caractéristiques"""
        total_cost = 0
        for char_name, value in values.items():
            total_cost += self._get_cost_for_value(value)
        return total_cost

    def _get_cost_for_value(self, value: int) -> int:
        """Calcule le coût progressif pour une valeur donnée"""
        total_cost = 0
        current_value = 1  # On commence à 1
        
        # Trier les plages de coût par ordre croissant
        sorted_ranges = sorted(self.cost_table.items(), 
                             key=lambda x: int(x[0].split('-')[0]) if '-' in x[0] else int(x[0]))
        
        # Calculer le coût progressif pour chaque plage
        for range_key, cost_per_point in sorted_ranges:
            if current_value > value:
                break  # On a déjà atteint la valeur cible
            
            if "-" in range_key:
                start, end = map(int, range_key.split("-"))
                
                start_in_range = max(current_value, start)
                end_in_range = min(value, end)
                
                if start_in_range <= end_in_range:
                    points_in_this_range = end_in_range - start_in_range + 1
                    total_cost += points_in_this_range * cost_per_point
                    current_value = end_in_range + 1
            else:
                # Valeur exacte
                exact_value = int(range_key)
                if current_value <= exact_value <= value:
                    total_cost += cost_per_point
                    current_value = exact_value + 1
        
        return total_cost

    def set_racial_bonus(self, characteristic: str, bonus: int):
        """Définit un bonus racial pour une caractéristique"""
        if characteristic in self.names:
            self.racial_bonuses[characteristic] = bonus

    def set_value(self, characteristic: str, value: int):
        """Définit la valeur d'une caractéristique"""
        if characteristic in self.names:
            self.values[characteristic] = value

    def get_all_characteristics(self) -> Dict:
        """Retourne le fichier characteristics.json complet"""
        return {
            "characteristics": self.characteristics_info,
            "bonus_table": self.bonus_table,
            "cost_table": self.cost_table,
            "starting_points": self.starting_points
        }

    def get_all_characteristics_with_values(self) -> Dict[str, Dict]:
        """Retourne toutes les caractéristiques avec leurs informations et valeurs actuelles"""
        result = {}
        for name in self.names:
            result[name] = {
                "name": name,
                "description": self.get_description(name),
                "value": self.values.get(name, 50),
                "racial_bonus": self.racial_bonuses.get(name, 0),
                "final_bonus": self.get_bonus(name),
                "info": self.characteristics_info.get(name, {})
            }
        return result
