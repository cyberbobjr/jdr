"""
Service spécialisé pour le chargement et la sauvegarde des données de personnage.
Respect du SRP - Responsabilité unique : gestion des données persistantes.
"""

import os
from typing import List, Optional
from uuid import UUID
from back.models.domain.character_v2 import CharacterV2, Stats, Skills, CombatStats, Equipment, Spells
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
    
    def load_character(self, character_id: Optional[str] = None) -> CharacterV2:
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
        
        state_data = CharacterPersistenceService.load_character_data(target_id)
        
        # If already v2-shaped, validate directly
        try:
            if isinstance(state_data, dict) and "combat_stats" in state_data and "stats" in state_data:
                character = CharacterV2.model_validate(state_data)
                log_debug("Personnage V2 chargé avec succès", action="load_character_v2", character_id=target_id)
                return character
        except Exception:
            pass

        # Legacy shape -> convert to V2 with sensible defaults
        name = state_data.get("name") or "Unnamed"
        race = state_data.get("race")
        if isinstance(race, dict):
            race = race.get("name", "Unknown")
        culture = state_data.get("culture")
        if isinstance(culture, dict):
            culture = culture.get("name", "Unknown")

        try:
            char_id = UUID(str(state_data.get("id", target_id)))
        except Exception:
            char_id = None

        legacy_stats = state_data.get("stats", {}) or {}
        stats = Stats(
            strength=int(legacy_stats.get("strength", legacy_stats.get("Force", 10) or 10)),
            constitution=int(legacy_stats.get("constitution", legacy_stats.get("Constitution", 10) or 10)),
            agility=int(legacy_stats.get("agility", legacy_stats.get("Agilité", 10) or 10)),
            intelligence=int(legacy_stats.get("intelligence", legacy_stats.get("Raisonnement", 10) or 10)),
            wisdom=int(legacy_stats.get("wisdom", legacy_stats.get("Volonté", 10) or 10)),
            charisma=int(legacy_stats.get("charisma", legacy_stats.get("Présence", 10) or 10)),
        )

        skills = Skills()  # Cannot reliably convert legacy flat skills -> default empty

        hp_legacy = int(state_data.get("hp", 100) or 100)
        combat_stats = CombatStats(
            max_hit_points=hp_legacy,
            current_hit_points=hp_legacy,
            max_mana_points=0,
            current_mana_points=0,
            armor_class=10,
            attack_bonus=0,
        )

        equipment = Equipment(gold=int(state_data.get("gold", 0) or 0))

        character = CharacterV2(
            id=char_id or CharacterV2.model_fields["id"].default_factory(),
            name=name,
            race=str(race or "Unknown"),
            culture=str(culture or "Unknown"),
            stats=stats,
            skills=skills,
            combat_stats=combat_stats,
            equipment=equipment,
            spells=Spells(),
            level=1,
            status=CharacterV2.model_fields["status"].default,
            experience_points=int(state_data.get("xp", 0) or 0),
        )

        log_debug("Personnage legacy converti en V2", action="load_character_convert_v2", character_id=target_id)
        return character
    
    def save_character(self, character: CharacterV2, character_id: Optional[str] = None) -> None:
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
        
        character_dict = character.model_dump()
        # Retirer l'ID car il ne doit pas être dans le fichier
        character_dict.pop('id', None)
        
        CharacterPersistenceService.save_character_data(target_id, character_dict)
        log_debug("Personnage sauvegardé", action="save_character", character_id=target_id)
    
    def get_all_characters(self) -> List[CharacterV2]:
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
    
    def get_character_by_id(self, character_id: str) -> CharacterV2:
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
