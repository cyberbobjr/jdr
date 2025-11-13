"""
Equipment manager for the role-playing game system.
Loads and exposes equipment data from YAML file.
"""

import yaml
import os
from typing import Dict, List, Optional, Any
from back.config import get_data_dir

class EquipmentManager:
    """
    Equipment manager for the game.
    """
    
    def __init__(self):
        """
        ### __init__
        **Description:** Initialize equipment manager and load data from YAML.
        **Parameters:** None
        **Returns:** None
        """
        self._equipment_data = self._load_equipment_data()
    
    def _load_equipment_data(self) -> Dict[str, Any]:
        """
        ### _load_equipment_data
        **Description:** Load equipment data from YAML file.
        **Parameters:** None
        **Returns:** Equipment data dictionary.
        """
        try:
            data_path = os.path.join(get_data_dir(), 'equipment.yaml')
            with open(data_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Equipment data file not found: {data_path}. "
                f"Please ensure that file exists and contains valid YAML data with equipment definitions."
            )
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Invalid YAML in equipment file {data_path}: {str(e)}. "
                f"Please check the file format and syntax."
            )
    
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
