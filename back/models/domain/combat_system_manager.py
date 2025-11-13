"""
Combat system manager for the role-playing game.
Loads and exposes combat rules from YAML file.
"""

import yaml
import os
from typing import Dict, Optional, Any
from back.config import get_data_dir

class CombatSystemManager:
    """
    Manager for combat system rules and data.
    """
    
    def __init__(self):
        """
        ### __init__
        **Description:** Initialize combat system manager and load data from YAML.
        **Parameters:** None
        **Returns:** None
        """
        self._combat_data = self._load_combat_data()
    
    def _load_combat_data(self) -> Dict[str, Any]:
        """
        ### _load_combat_data
        **Description:** Load combat system data from YAML file.
        **Parameters:** None
        **Returns:** Combat data dictionary.
        """
        try:
            data_path = os.path.join(get_data_dir(), 'combat_system.yaml')
            with open(data_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Combat system data file not found: {data_path}. "
                f"Please ensure that file exists and contains valid YAML data with combat system rules."
            )
        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Invalid YAML in combat system file {data_path}: {str(e)}. "
                f"Please check the file format and syntax."
            )
    
    def get_initiative_rules(self) -> Dict[str, Any]:
        """
        ### get_initiative_rules
        **Description:** Retourne les règles d'initiative.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire des règles d'initiative.
        """
        return self._combat_data.get("initiative", {})
    
    def get_turn_structure(self) -> Dict[str, Any]:
        """
        ### get_turn_structure
        **Description:** Retourne la structure d'un tour de combat.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire de la structure de tour.
        """
        return self._combat_data.get("turn_structure", {})
    
    def get_all_actions(self) -> Dict[str, Dict[str, Any]]:
        """
        ### get_all_actions
        **Description:** Retourne toutes les actions de combat disponibles.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire des actions {action_id: données}.
        """
        return self._combat_data.get("actions", {})
    
    def get_action_by_id(self, action_id: str) -> Optional[Dict[str, Any]]:
        """
        ### get_action_by_id
        **Description:** Recherche une action de combat par son ID.
        **Paramètres:**
        - `action_id` (str): Identifiant de l'action recherchée.
        **Retour:** Dictionnaire des données de l'action ou None si non trouvée.
        """
        return self._combat_data.get("actions", {}).get(action_id)
    
    def get_difficulty_modifiers(self) -> Dict[str, int]:
        """
        ### get_difficulty_modifiers
        **Description:** Retourne les modificateurs de difficulté.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire {difficulté: modificateur}.
        """
        return self._combat_data.get("difficulty_modifiers", {})
    
    def get_difficulty_modifier(self, difficulty: str) -> int:
        """
        ### get_difficulty_modifier
        **Description:** Retourne le modificateur pour une difficulté donnée.
        **Paramètres:**
        - `difficulty` (str): Nom de la difficulté.
        **Retour:** Modificateur numérique (0 si difficulté inconnue).
        """
        return self._combat_data.get("difficulty_modifiers", {}).get(difficulty.lower(), 0)
    
    def get_damage_types(self) -> Dict[str, Dict[str, Any]]:
        """
        ### get_damage_types
        **Description:** Retourne les types de dégâts disponibles.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire des types de dégâts.
        """
        return self._combat_data.get("damage_types", {})
    
    def get_armor_types(self) -> Dict[str, Dict[str, Any]]:
        """
        ### get_armor_types
        **Description:** Retourne les types d'armure disponibles.
        **Paramètres:** Aucun
        **Retour:** Dictionnaire des types d'armure.
        """
        return self._combat_data.get("armor_types", {})
    
    def calculate_initiative(self, agility_value: int, dice_roll: Optional[int] = None) -> int:
        """
        ### calculate_initiative
        **Description:** Calcule l'initiative selon les règles définies.
        **Paramètres:**
        - `agility_value` (int): Valeur d'Agilité du personnage.
        - `dice_roll` (int): Résultat du dé (optionnel, généré automatiquement si None).
        **Retour:** Valeur d'initiative calculée.
        """
        if dice_roll is None:
            import random
            dice_roll = random.randint(1, 20)
        
        return agility_value + dice_roll
