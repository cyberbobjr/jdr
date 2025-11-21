"""
Equipment manager for the role-playing game system.
Loads and exposes equipment data from YAML file and exposes a
standardized item schema for use by services.

Canonical item keys:
- id (str): slug generated from name (lowercase, hyphens)
- name (str)
- category (str): one of 'weapon', 'armor', 'accessory', 'consumable'
- cost (float)
- weight (float)
- quantity (int, default 1)
- equipped (bool, default False)

Optional keys preserved from source data (not normalized beyond passthrough):
- damage (str), range (int|str) for weapons
- protection (int) for armor
- description (str), type (str)
"""

import yaml
import os
from typing import Dict, List, Optional, Any
import re
from back.config import get_data_dir

class EquipmentManager:
    """
    Equipment manager for the game.

    Purpose:
        Manages all equipment data loaded from YAML configuration files.
        This manager provides standardized access to weapons, armor, accessories, and
        consumables, ensuring consistent item schemas across the application. It handles
        data normalization, category classification, and item lookup operations, enabling
        services and tools to work with equipment without directly parsing YAML files.

    Attributes:
        _equipment_data (Optional[Dict[str, Any]]): Raw equipment data loaded from YAML.
    """
    
    @property
    def equipment_data(self) -> Dict[str, Any]:
        """Lazy load equipment data."""
        if self._equipment_data is None:
            self._equipment_data = self._load_equipment_data()
        return self._equipment_data
    
    def __init__(self):
        """
        ### __init__
        **Description:** Initialize equipment manager. Data is loaded lazily.
        **Parameters:** None
        **Returns:** None
        """
        self._equipment_data = None
    
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
            
    def get_all_equipment(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Return all equipment as standardized dictionaries grouped by categories.

        Parameters:
        - None

        Returns:
        - Dict[str, List[Dict[str, Any]]]: Dictionary with keys 'weapons', 'armor', 'accessories', 'consumables'.

        Example output item (weapon):
        {
            "id": "longsword",
            "name": "Longsword",
            "category": "weapon",
            "cost": 2.0,
            "weight": 1.5,
            "quantity": 1,
            "equipped": False,
            "damage": "1d8+4",
            "description": "Balanced and versatile one-handed sword"
        }
        """
        return self._standardize_catalog(self.equipment_data)
    
    def get_equipment_names(self) -> List[str]:
        """
        ### get_equipment_names
        **Description:** Retourne uniquement les noms de tous les équipements.
        **Paramètres:** Aucun
        **Retour:** Liste des noms d'équipements.
        """
        all_names = []
        for category in self.equipment_data.values():
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
        return self.equipment_data.get("weapons", {})
    
    def get_armor(self) -> Dict[str, Dict[str, Any]]:
        """
        ### get_armor
        **Description:** Retourne uniquement les armures.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire des armures.
        """
        return self.equipment_data.get("armor", {})
    
    def get_items(self) -> Dict[str, Dict[str, Any]]:
        """
        ### get_items
        **Description:** Retourne uniquement les objets divers.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire des objets.
        """
        return self.equipment_data.get("items", {})
    
    def get_equipment_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        ### get_equipment_by_name
        **Description:** Recherche un équipement par son nom.
        **Paramètres:**
        - `name` (str): Nom de l'équipement recherché.
        **Retour:** Dictionnaire des données de l'équipement ou None si non trouvé.        """
        for category in self.equipment_data.values():
            if isinstance(category, dict) and name in category:
                return category[name]
        return None

    # --- Standardization helpers ---
    @staticmethod
    def _slugify(name: str) -> str:
        s = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip()).strip("-").lower()
        return s

    def _standardize_item(self, name: str, src: Dict[str, Any], category_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Standardize a raw YAML item to canonical dict with required keys.
        Category resolution:
        - 'weapons' group -> category 'weapon'
        - 'armor' group -> category 'armor'
        - 'items' group -> if type == 'consumable' -> 'consumable', else 'accessory'
        """
        category = category_hint
        if category_hint == 'weapons':
            category = 'weapon'
        elif category_hint == 'armor':
            category = 'armor'
        elif category_hint == 'items':
            category = 'consumable' if str(src.get('type', '')).lower() == 'consumable' else 'accessory'

        out: Dict[str, Any] = {
            'id': self._slugify(name),
            'name': name,
            'category': category or str(src.get('type', '')).lower() or 'accessory',
            'cost': float(src.get('cost', 0)),
            'weight': float(src.get('weight', 0)),
            'quantity': 1,
            'equipped': False,
        }
        # Preserve common optional fields without renaming
        for key in ('damage', 'range', 'protection', 'description', 'type'):
            if key in src:
                out[key] = src[key]
        return out

    def _standardize_catalog(self, data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        weapons = []
        armor = []
        accessories = []
        consumables = []

        for group_name, group in data.items():
            # Skip non-dict groups and metadata sections
            if not isinstance(group, dict) or str(group_name).startswith('_'):
                continue
            for item_name, item_data in group.items():
                # Skip entries that are not proper item dictionaries (e.g., metadata strings)
                if not isinstance(item_data, dict):
                    continue
                std = self._standardize_item(item_name, item_data, category_hint=group_name)
                if std['category'] == 'weapon':
                    weapons.append(std)
                elif std['category'] == 'armor':
                    armor.append(std)
                elif std['category'] == 'consumable':
                    consumables.append(std)
                else:
                    accessories.append(std)

        return {
            'weapons': weapons,
            'armor': armor,
            'accessories': accessories,
            'consumables': consumables,
        }

    def get_equipment_by_id(self, id_or_name: str) -> Optional[Dict[str, Any]]:
        """
        Lookup an equipment item by canonical id (slug) or exact name, case-insensitive.
        Returns standardized item dict or None.
        """
        catalog = self._standardize_catalog(self.equipment_data)
        target = id_or_name.strip().lower()
        for lst in (catalog['weapons'], catalog['armor'], catalog['accessories'], catalog['consumables']):
            for it in lst:
                if it['id'] == target or it['name'].lower() == target:
                    return it
        return None
