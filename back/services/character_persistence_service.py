"""
Service de persistance centralisé pour les fichiers JSON des personnages.
Factorisation du code de lecture/écriture utilisé par CharacterService et autres services.
"""

import os
import json
from typing import Dict, Any
from back.utils.logger import log_debug
from back.config import get_data_dir


class CharacterPersistenceService:
    """
    ### CharacterPersistenceService
    **Description :** Service centralisé pour la persistance des fichiers JSON des personnages.
    Factorise toutes les opérations CRUD sur les fichiers de personnages.
    """
    
    @staticmethod
    def _get_character_file_path(character_id: str) -> str:
        """
        ### _get_character_file_path
        **Description :** Construit le chemin complet vers le fichier JSON d'un personnage.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        **Retour :** Chemin complet vers le fichier JSON (str).
        """
        characters_dir = os.path.join(get_data_dir(), "characters")
        path = os.path.join(characters_dir, f"{character_id}.json")
        print(f"[DEBUG BACKEND] get_data_dir()={get_data_dir()} | character_id={character_id} | path={path}")
        return path
    
    @staticmethod
    def character_exists(character_id: str) -> bool:
        """
        ### character_exists
        **Description :** Vérifie si un fichier personnage existe.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        **Retour :** True si le fichier existe, False sinon (bool).
        """
        filepath = CharacterPersistenceService._get_character_file_path(character_id)
        return os.path.exists(filepath)
    
    @staticmethod
    def load_character_data(character_id: str) -> Dict[str, Any]:
        """
        ### load_character_data
        **Description :** Charge les données complètes d'un personnage depuis son fichier JSON.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        **Retour :** Données complètes du personnage (dict).
        **Raises :** FileNotFoundError si le personnage n'existe pas.
        """
        filepath = CharacterPersistenceService._get_character_file_path(character_id)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Le personnage {character_id} n'existe pas.")
        
        try:
            with open(filepath, "r", encoding="utf-8") as file:
                character_data = json.load(file)
            
            log_debug("Données personnage chargées", 
                     action="load_character_data", 
                     character_id=character_id, 
                     filepath=os.path.abspath(filepath))
            
            return character_data
        
        except json.JSONDecodeError as e:
            log_debug("Erreur de décodage JSON", 
                     action="load_character_data_error", 
                     character_id=character_id, 
                     error=str(e))
            raise ValueError(f"Fichier JSON corrompu pour le personnage {character_id}: {str(e)}")
        
        except Exception as e:
            log_debug("Erreur lors du chargement", 
                     action="load_character_data_error", 
                     character_id=character_id, 
                     error=str(e))
            raise
    
    @staticmethod
    def save_character_data(character_id: str, character_data: Dict[str, Any]) -> None:
        """
        ### save_character_data
        **Description :** Sauvegarde les données complètes d'un personnage dans son fichier JSON.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        - `character_data` (dict) : Données à sauvegarder.
        **Retour :** Aucun
        """
        filepath = CharacterPersistenceService._get_character_file_path(character_id)
        
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(character_data, file, ensure_ascii=False, indent=2)
            
            log_debug("Données personnage sauvegardées", 
                     action="save_character_data", 
                     character_id=character_id, 
                     filepath=os.path.abspath(filepath))
        
        except Exception as e:
            log_debug("Erreur lors de la sauvegarde", 
                     action="save_character_data_error", 
                     character_id=character_id, 
                     error=str(e))
            raise
