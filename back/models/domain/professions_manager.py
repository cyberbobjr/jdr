"""
Gestionnaire des professions pour le système de jeu de rôle.
Charge et expose les données des professions depuis le fichier JSON.
"""

import json
import os
from typing import Dict, List, Optional, Any
from back.config import get_data_dir

class ProfessionsManager:
    """
    Gestionnaire pour les professions du jeu.
    """
    
    def __init__(self):
        """
        ### __init__
        **Description:** Initialise le gestionnaire des professions et charge les données depuis le JSON.
        **Paramètres:** Aucun
        **Retour:** Aucun
        """
        self._professions_data = self._load_professions_data()
    
    def _load_professions_data(self) -> List[Dict[str, Any]]:
        """
        ### _load_professions_data
        **Description:** Charge les données des professions depuis le fichier JSON.
        **Paramètres:** Aucun
        **Retour:** Liste des professions avec leurs données complètes.
        """
        try:
            data_path = os.path.join(get_data_dir(), 'professions.json')
            with open(data_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # Données de fallback minimales
            return [
                {
                    "name": "Aventurier",
                    "description": "Profession généraliste",
                    "primary_characteristics": ["Force", "Agilité", "Volonté"],
                    "skill_groups": {},
                    "magic_spheres": [],
                    "starting_equipment": []
                }
            ]
    
    def get_all_professions(self) -> List[Dict[str, Any]]:
        """
        ### get_all_professions
        **Description:** Retourne toutes les professions disponibles.
        **Paramètres:** Aucun
        **Retour:** Liste complète des professions.
        """
        return self._professions_data
    
    def get_profession_names(self) -> List[str]:
        """
        ### get_profession_names
        **Description:** Retourne uniquement les noms des professions.
        **Paramètres:** Aucun
        **Retour:** Liste des noms de professions.
        """
        return [profession["name"] for profession in self._professions_data]
    
    def get_profession_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        ### get_profession_by_name
        **Description:** Recherche une profession par son nom.
        **Paramètres:**
        - `name` (str): Nom de la profession recherchée.
        **Retour:** Dictionnaire des données de la profession ou None si non trouvée.
        """
        for profession in self._professions_data:
            if profession["name"] == name:
                return profession
        return None
    
    def get_skill_groups_for_profession(self, profession_name: str) -> Dict[str, Dict[str, int]]:
        """
        ### get_skill_groups_for_profession
        **Description:** Retourne les groupes de compétences d'une profession avec leurs coûts et rangs.
        **Paramètres:**
        - `profession_name` (str): Nom de la profession.
        **Retour:** Dictionnaire des groupes de compétences {groupe: {ranks: int, cost_per_rank: int}}.
        """
        profession = self.get_profession_by_name(profession_name)
        if profession:
            return profession.get("skill_groups", {})
        return {}
    
    def get_magic_spheres_for_profession(self, profession_name: str) -> List[str]:
        """
        ### get_magic_spheres_for_profession
        **Description:** Retourne les sphères magiques accessibles pour une profession.
        **Paramètres:**
        - `profession_name` (str): Nom de la profession.
        **Retour:** Liste des sphères magiques.
        """
        profession = self.get_profession_by_name(profession_name)
        if profession:
            return profession.get("magic_spheres", [])
        return []
    
    def get_starting_equipment_for_profession(self, profession_name: str) -> List[str]:
        """
        ### get_starting_equipment_for_profession
        **Description:** Retourne l'équipement de départ d'une profession.
        **Paramètres:**
        - `profession_name` (str): Nom de la profession.
        **Retour:** Liste de l'équipement de départ.
        """
        profession = self.get_profession_by_name(profession_name)
        if profession:
            return profession.get("starting_equipment", [])
        return []
    
    def get_primary_characteristics_for_profession(self, profession_name: str) -> List[str]:
        """
        ### get_primary_characteristics_for_profession
        **Description:** Retourne les caractéristiques principales d'une profession.
        **Paramètres:**
        - `profession_name` (str): Nom de la profession.
        **Retour:** Liste des caractéristiques principales.
        """
        profession = self.get_profession_by_name(profession_name)
        if profession:
            return profession.get("primary_characteristics", [])
        return []
