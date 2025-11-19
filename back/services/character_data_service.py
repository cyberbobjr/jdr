"""
Service spécialisé pour le chargement et la sauvegarde des données de personnage.
Respect du SRP - Responsabilité unique : gestion des données persistantes.
"""

import os
import json
from typing import List, Optional
from back.models.domain.character import Character
from back.utils.logger import log_debug
from back.config import get_data_dir


class CharacterDataService:
    """
    ### CharacterDataService
    **Description:** Service spécialisé dans le chargement et la sauvegarde des données de personnage.
    **Responsabilité unique:** Gestion des opérations de persistance des données Character.
    """
    
    def __init__(self):
        """
        ### __init__
        **Description:** Initialise le service de données de personnage.
        """
        pass

    def _get_characters_dir(self) -> str:
        return os.path.join(get_data_dir(), "characters")

    def _get_character_file_path(self, character_id: str) -> str:
        if not character_id or not isinstance(character_id, str) or not character_id.strip():
            raise ValueError("Character ID must be a non-empty string")
        return os.path.join(self._get_characters_dir(), f"{character_id}.json")
    
    def load_character(self, character_id: str) -> Character:
        """
        ### load_character
        **Description:** Charge un personnage à partir de son identifiant.
        **Paramètres:**
        - `character_id` (str): Identifiant du personnage
        **Retour:** Objet Character chargé
        **Lève:** FileNotFoundError si le personnage n'existe pas
        """
        if not character_id:
            raise ValueError("Aucun character_id fourni")

        filepath = self._get_character_file_path(character_id)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Le personnage {character_id} n'existe pas.")

        try:
            with open(filepath, "r", encoding="utf-8") as file:
                character_data = json.load(file)

            log_debug("Personnage chargé avec succès", action="load_character", character_id=character_id)
            return Character(**character_data)

        except json.JSONDecodeError as e:
            log_debug("Erreur de décodage JSON",
                     action="load_character_error",
                     character_id=character_id,
                     error=str(e))
            raise ValueError(f"Fichier JSON corrompu pour le personnage {character_id}: {str(e)}")
        except Exception as e:
            log_debug("Erreur lors du chargement",
                     action="load_character_error",
                     character_id=character_id,
                     error=str(e))
            raise
    
    def save_character(self, character: Character, character_id: Optional[str] = None) -> Character:
        """
        ### save_character
        **Description:** Sauvegarde un personnage vers le stockage persistant.
        **Paramètres:**
        - `character` (Character): Objet Character à sauvegarder
        - `character_id` (Optional[str]): Identifiant du personnage (optionnel si présent dans l'objet character)
        **Retour:** Le personnage sauvegardé (avec merge éventuel)
        """
        # Si character_id n'est pas fourni, on essaie de le récupérer depuis l'objet character
        target_id = character_id
        if not target_id and hasattr(character, 'id'):
            target_id = str(character.id)
            
        if not target_id:
            raise ValueError("Aucun character_id fourni et impossible de le récupérer depuis l'objet Character")
        
        filepath = self._get_character_file_path(target_id)

        try:
            # Charger les données existantes si le fichier existe pour merger
            existing_data: dict = {}
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as file:
                        existing_data = json.load(file)
                except (json.JSONDecodeError, Exception) as e:
                    log_debug("Erreur lors de la lecture du fichier existant, recréation",
                             action="save_character_warning",
                             character_id=target_id,
                             error=str(e))
                    existing_data = {}

            # Convertir le Character en dict avec mode='json' pour sérialisation JSON
            character_dict: dict = character.model_dump(mode='json')

            # Merger les données (les nouvelles données ont priorité)
            merged_data: dict = {**existing_data, **character_dict}

            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(merged_data, file, ensure_ascii=False, indent=2)

            log_debug("Personnage sauvegardé", action="save_character", character_id=target_id)
            
            return Character(**merged_data)

        except Exception as e:
            log_debug("Erreur lors de la sauvegarde",
                     action="save_character_error",
                     character_id=target_id,
                     error=str(e))
            raise
    
    def get_all_characters(self) -> List[Character]:
        """
        ### get_all_characters
        **Description:** Récupère la liste de tous les personnages disponibles.
        **Retour:** Liste d'objets Character
        """
        characters = []
        characters_dir = self._get_characters_dir()
        
        if not os.path.exists(characters_dir):
            log_debug("Répertoire characters inexistant", action="get_all_characters")
            return characters
        
        for filename in os.listdir(characters_dir):
            if filename.endswith(".json"):
                character_id = filename[:-5]  # Retire l'extension .json
                try:
                    character = self.load_character(character_id)
                    characters.append(character)
                except (FileNotFoundError, ValueError) as e:
                    log_debug("Erreur lors du chargement du personnage", 
                             action="get_all_characters_error", 
                             filename=filename, 
                             error=str(e))
                    continue
        
        log_debug("Chargement de tous les personnages", action="get_all_characters", count=len(characters))
        return characters
    
    def get_character_by_id(self, character_id: str) -> Character:
        """
        ### get_character_by_id
        **Description:** Récupère un personnage à partir de son identifiant.
        **Paramètres:**
        - `character_id` (str): Identifiant du personnage
        **Retour:** Objet Character
        **Lève:** FileNotFoundError si le personnage n'existe pas
        """
        return self.load_character(character_id)
    
    def character_exists(self, character_id: str) -> bool:
        """
        ### character_exists
        **Description:** Vérifie si un personnage existe.
        **Paramètres:**
        - `character_id` (str): Identifiant du personnage
        **Retour:** True si le personnage existe, False sinon
        """
        try:
            filepath = self._get_character_file_path(character_id)
            return os.path.exists(filepath)
        except ValueError:
            return False

    def delete_character(self, character_id: str) -> None:
        """
        ### delete_character
        **Description:** Supprime le fichier d'un personnage.
        **Paramètres:**
        - `character_id` (str): Identifiant du personnage
        **Retour:** Aucun
        """
        filepath = self._get_character_file_path(character_id)
        if os.path.exists(filepath):
            os.remove(filepath)
            log_debug("Personnage supprimé", action="delete_character", character_id=character_id)
        else:
            log_debug("Suppression ignorée: personnage introuvable", action="delete_character", character_id=character_id)
