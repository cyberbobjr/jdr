"""
Service de persistance centralisé pour les fichiers JSON des personnages.
Factorisation du code de lecture/écriture utilisé par CharacterService et autres services.
"""

import os
import json
from typing import Dict, Any
from dataclasses import asdict, is_dataclass
from back.utils.logger import log_debug
from back.config import get_data_dir

CHARACTERS_DIR = os.path.join(get_data_dir(), "characters")


class CharacterPersistenceService:
    """
    ### CharacterPersistenceService
    **Description :** Service centralisé pour la persistance des fichiers JSON des personnages.
    Factorise toutes les opérations CRUD sur les fichiers de personnages.
    """

    @staticmethod
    def _validate_character_id(character_id) -> str:
        """
        ### _validate_character_id
        **Description :** Valide l'identifiant du personnage.
        **Paramètres :**
        - `character_id` : Identifiant à valider.
        **Retour :** L'identifiant validé (str).
        **Raises :** ValueError si l'identifiant est invalide.
        """
        if character_id is None or not isinstance(character_id, str) or not character_id.strip():
            raise ValueError("Character ID must be a non-empty string")
        return character_id

    @staticmethod
    def _get_character_file_path(character_id: str) -> str:
        """
        ### _get_character_file_path
        **Description :** Construit le chemin complet vers le fichier JSON d'un personnage.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        **Retour :** Chemin complet vers le fichier JSON (str).
        """
        CharacterPersistenceService._validate_character_id(character_id)
        path = os.path.join(CHARACTERS_DIR, f"{character_id}.json")
        print(f"[DEBUG BACKEND] CHARACTERS_DIR={CHARACTERS_DIR} | character_id={character_id} | path={path}")
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
    def save_character_data(character_id: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ### save_character_data
        **Description :** Sauvegarde les données complètes d'un personnage dans son fichier JSON.
        Effectue un merge avec les données existantes pour éviter l'écrasement.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        - `character_data` (dict) : Données à sauvegarder.
        **Retour :** Les données complètes fusionnées du personnage (dict).
        """
        filepath = CharacterPersistenceService._get_character_file_path(character_id)
        
        try:
            # Charger les données existantes si le fichier existe
            existing_data = {}
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as file:
                        existing_data = json.load(file)
                except (json.JSONDecodeError, Exception) as e:
                    log_debug("Erreur lors de la lecture du fichier existant, recréation", 
                             action="save_character_data_warning", 
                             character_id=character_id, 
                             error=str(e))
                    existing_data = {}
            
            # Merger les données (les nouvelles données ont priorité)
            merged_data = {**existing_data, **character_data}
            
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(merged_data, file, ensure_ascii=False, indent=2)
            
            log_debug("Données personnage sauvegardées (merge)", 
                     action="save_character_data", 
                     character_id=character_id, 
                     filepath=os.path.abspath(filepath),
                     keys_updated=list(character_data.keys()))
            return merged_data
        except Exception as e:
            log_debug("Erreur lors de la sauvegarde", 
                     action="save_character_data_error", 
                     character_id=character_id, 
                     error=str(e))
            raise
    
    @staticmethod
    def delete_character_data(character_id: str) -> None:
        """
        ### delete_character_data
        **Description :** Supprime le fichier JSON d'un personnage à partir de son identifiant.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        **Retour :** Aucun
        """
        filepath = CharacterPersistenceService._get_character_file_path(character_id)
        if os.path.exists(filepath):
            os.remove(filepath)
            log_debug("Personnage supprimé", action="delete_character_data", character_id=character_id, filepath=filepath)
        else:
            log_debug("Suppression ignorée : personnage introuvable", action="delete_character_data", character_id=character_id, filepath=filepath)
    
    @staticmethod
    def _serialize_for_json(obj):
        """
        ### _serialize_for_json
        **Description :** Convertit récursivement les objets dataclass en dictionnaires pour la sérialisation JSON.
        **Paramètres :**
        - `obj` : L'objet à sérialiser
        **Retour :** L'objet sérialisable en JSON
        """
        if is_dataclass(obj):
            return asdict(obj)
        elif isinstance(obj, dict):
            return {k: CharacterPersistenceService._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [CharacterPersistenceService._serialize_for_json(item) for item in obj]
        else:
            return obj
