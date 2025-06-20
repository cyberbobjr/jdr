"""
Gestionnaire des équipements pour le système de jeu de rôle.
Charge et expose les données des équipements depuis le fichier JSON.
"""

import json
import os
from typing import Dict, List, Optional, Any
from back.config import get_data_dir

class EquipmentManager:
    """
    Gestionnaire pour les équipements du jeu.
    """
    
    def __init__(self):
        """
        ### __init__
        **Description:** Initialise le gestionnaire des équipements et charge les données depuis le JSON.
        **Paramètres:** Aucun
        **Retour:** Aucun
        """
        self._equipment_data = self._load_equipment_data()
    
    def _load_equipment_data(self) -> Dict[str, Any]:
        """
        ### _load_equipment_data
        **Description:** Charge les données des équipements depuis le fichier JSON.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire des équipements.
        """
        try:
            data_path = os.path.join(get_data_dir(), 'equipment.json')
            with open(data_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # Données de fallback minimales
            return {
                "weapons": {
                    "Épée longue": {
                        "type": "arme",
                        "category": "mêlée",
                        "damage": "1d8+4",
                        "weight": 1.5,
                        "cost": 50
                    },
                    "Arc long": {
                        "type": "arme",
                        "category": "distance",
                        "damage": "1d8+2",
                        "range": 150,
                        "weight": 1.0,
                        "cost": 30
                    }
                },
                "armor": {
                    "Armure de cuir": {
                        "type": "armure",
                        "protection": 3,
                        "weight": 5.0,
                        "cost": 25
                    },
                    "Cotte de mailles": {
                        "type": "armure",
                        "protection": 6,
                        "weight": 15.0,
                        "cost": 100
                    }
                },
                "items": {
                    "Corde (10m)": {
                        "type": "équipement",
                        "weight": 2.0,
                        "cost": 5
                    },
                    "Rations (1 jour)": {
                        "type": "consommable",
                        "weight": 0.5,
                        "cost": 2
                    }
                }
            }
    
    def get_all_equipment(self) -> Dict[str, Any]:
        """
        ### get_all_equipment
        **Description:** Retourne tous les équipements disponibles.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire complet des équipements.
        """
        return self._equipment_data
    
    def get_equipment_names(self) -> List[str]:
        """
        ### get_equipment_names
        **Description:** Retourne uniquement les noms de tous les équipements.
        **Paramètres:** Aucun
        **Retour:** Liste des noms d'équipements.
        """
        all_names = []
        for category in self._equipment_data.values():
            if isinstance(category, dict):
                all_names.extend(category.keys())
        return all_names
    
    def get_weapons(self) -> Dict[str, Dict[str, Any]]:
        """
        ### get_weapons
        **Description:** Retourne uniquement les armes.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire des armes.
        """
        return self._equipment_data.get("weapons", {})
    
    def get_armor(self) -> Dict[str, Dict[str, Any]]:
        """
        ### get_armor
        **Description:** Retourne uniquement les armures.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire des armures.
        """
        return self._equipment_data.get("armor", {})
    
    def get_items(self) -> Dict[str, Dict[str, Any]]:
        """
        ### get_items
        **Description:** Retourne uniquement les objets divers.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire des objets.
        """
        return self._equipment_data.get("items", {})
    
    def get_equipment_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        ### get_equipment_by_name
        **Description:** Recherche un équipement par son nom.
        **Paramètres:**
        - `name` (str): Nom de l'équipement recherché.
        **Retour:** Dictionnaire des données de l'équipement ou None si non trouvé.        """
        for category in self._equipment_data.values():
            if isinstance(category, dict) and name in category:
                return category[name]
        return None
