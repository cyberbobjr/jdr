"""
Service de persistance centralisé pour les fichiers JSON des personnages.
Factorisation du code de lecture/écriture utilisé par CharacterService et autres services.
"""

import os
import json
from typing import Dict, Any
from back.utils.logger import log_debug


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
        characters_dir = os.path.join(os.path.dirname(__file__), "../../data/characters")
        return os.path.join(characters_dir, f"{character_id}.json")
    
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
    def load_character_state(character_id: str) -> Dict[str, Any]:
        """
        ### load_character_state
        **Description :** Charge uniquement la section 'state' d'un personnage.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        **Retour :** Section 'state' du personnage (dict).
        **Raises :** FileNotFoundError si le personnage n'existe pas.
        """
        character_data = CharacterPersistenceService.load_character_data(character_id)
        state = character_data.get("state", {})
        
        log_debug("État personnage chargé", 
                 action="load_character_state", 
                 character_id=character_id, 
                 state_keys=list(state.keys()))
        
        return state
    
    @staticmethod
    def save_character_data(character_id: str, character_data: Dict[str, Any], 
                          operation: str = "update") -> None:
        """
        ### save_character_data
        **Description :** Sauvegarde les données complètes d'un personnage dans son fichier JSON.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        - `character_data` (dict) : Données complètes du personnage à sauvegarder.
        - `operation` (str) : Type d'opération pour le logging (défaut: "update").
        **Retour :** Aucun.
        """
        filepath = CharacterPersistenceService._get_character_file_path(character_id)
        
        try:
            with open(filepath, "w", encoding="utf-8") as file:
                json.dump(character_data, file, ensure_ascii=False, indent=2)
            
            log_debug("Données personnage sauvegardées", 
                     action=f"save_character_data_{operation}", 
                     character_id=character_id, 
                     filepath=os.path.abspath(filepath))
        
        except Exception as e:
            log_debug("Erreur lors de la sauvegarde", 
                     action=f"save_character_data_{operation}_error", 
                     character_id=character_id, 
                     error=str(e))
            raise
    
    @staticmethod
    def update_character_state(character_id: str, state_updates: Dict[str, Any], 
                              operation: str = "update") -> Dict[str, Any]:
        """
        ### update_character_state
        **Description :** Met à jour la section 'state' d'un personnage et sauvegarde le fichier.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        - `state_updates` (dict) : Mises à jour à appliquer à la section 'state'.
        - `operation` (str) : Type d'opération pour le logging (défaut: "update").
        **Retour :** Section 'state' mise à jour (dict).
        **Raises :** FileNotFoundError si le personnage n'existe pas.
        """
        # Charger les données existantes
        character_data = CharacterPersistenceService.load_character_data(character_id)
        
        # Mettre à jour la section state
        state = character_data.get("state", {})
        state.update(state_updates)
        character_data["state"] = state
        
        # Mettre à jour le timestamp de dernière modification
        from datetime import datetime
        character_data["last_update"] = datetime.now().isoformat()
        
        # Sauvegarder
        CharacterPersistenceService.save_character_data(character_id, character_data, operation)
        
        log_debug("État personnage mis à jour", 
                 action=f"update_character_state_{operation}", 
                 character_id=character_id, 
                 updated_keys=list(state_updates.keys()))
        
        return state
    
    @staticmethod
    def modify_character_attribute(character_id: str, attribute: str, 
                                 modifier_func, operation: str = "modify") -> Any:
        """
        ### modify_character_attribute
        **Description :** Modifie un attribut spécifique dans la section 'state' d'un personnage.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        - `attribute` (str) : Nom de l'attribut à modifier.
        - `modifier_func` (callable) : Fonction qui prend la valeur actuelle et retourne la nouvelle valeur.
        - `operation` (str) : Type d'opération pour le logging (défaut: "modify").
        **Retour :** Nouvelle valeur de l'attribut (Any).
        **Raises :** FileNotFoundError si le personnage n'existe pas.
        """
        # Charger l'état actuel
        state = CharacterPersistenceService.load_character_state(character_id)
        
        # Appliquer la modification
        current_value = state.get(attribute, 0)
        new_value = modifier_func(current_value)
        
        # Mettre à jour
        state_updates = {attribute: new_value}
        updated_state = CharacterPersistenceService.update_character_state(
            character_id, state_updates, f"{operation}_{attribute}")
        
        log_debug("Attribut personnage modifié", 
                 action=f"modify_character_attribute_{operation}", 
                 character_id=character_id, 
                 attribute=attribute, 
                 old_value=current_value, 
                 new_value=new_value)
        
        return new_value
