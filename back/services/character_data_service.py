"""
Service spécialisé pour le chargement et la sauvegarde des données de personnage.
Respect du SRP - Responsabilité unique : gestion des données persistantes.
"""

import os
from typing import List, Optional
from back.models.domain.character import Character
from back.services.character_persistence_service import CharacterPersistenceService
from back.utils.logger import log_debug
from back.config import get_data_dir


class CharacterDataService:
    """
    ### CharacterDataService
    **Description:** Service spécialisé dans le chargement et la sauvegarde des données de personnage.
    **Responsabilité unique:** Gestion des opérations de persistance des données Character.
    """
    
    def __init__(self, character_id: Optional[str] = None):
        """
        ### __init__
        **Description:** Initialise le service de données de personnage.
        **Paramètres:**
        - `character_id` (Optional[str]): Identifiant du personnage (optionnel pour les opérations globales)
        """
        self.character_id = character_id
    
    def load_character(self, character_id: Optional[str] = None) -> Character:
        """
        ### load_character
        **Description:** Charge un personnage à partir de son identifiant.
        **Paramètres:**
        - `character_id` (Optional[str]): Identifiant du personnage (utilise self.character_id si None)
        **Retour:** Objet Character chargé
        **Lève:** FileNotFoundError si le personnage n'existe pas
        """
        target_id = character_id or self.character_id
        if not target_id:
            raise ValueError("Aucun character_id fourni")

        character = CharacterPersistenceService.load_character_data(target_id)

        log_debug("Personnage chargé avec succès", action="load_character", character_id=target_id)
        return character
    
    def save_character(self, character: Character, character_id: Optional[str] = None) -> None:
        """
        ### save_character
        **Description:** Sauvegarde un personnage vers le stockage persistant.
        **Paramètres:**
        - `character` (Character): Objet Character à sauvegarder
        - `character_id` (Optional[str]): Identifiant du personnage (utilise self.character_id si None)
        **Retour:** Aucun
        """
        target_id = character_id or self.character_id
        if not target_id:
            raise ValueError("Aucun character_id fourni")
        
        CharacterPersistenceService.save_character_data(target_id, character)
        log_debug("Personnage sauvegardé", action="save_character", character_id=target_id)
    
    def get_all_characters(self) -> List[Character]:
        """
        ### get_all_characters
        **Description:** Récupère la liste de tous les personnages disponibles.
        **Retour:** Liste d'objets Character
        """
        characters = []
        characters_dir = os.path.join(get_data_dir(), "characters")
        
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
            self.load_character(character_id)
            return True
        except (FileNotFoundError, ValueError):
            return False
