# Logique métier unitaire (SRP)

import os
import json
import uuid
from typing import List
from back.models.schema import Character
from back.utils.logger import log_debug

class CharacterService:
    @staticmethod
    def get_all_characters() -> List[Character]:
        """
        Récupère la liste de tous les personnages disponibles à partir des fichiers JSON.

        Returns:
            List[Character]: Une liste d'objets Character représentant les personnages disponibles.
        """
        characters = []
        characters_dir = os.path.join(os.path.dirname(__file__), "../../data/characters")
        required_fields = ["name", "race", "culture", "profession", "caracteristiques", "competences"]
        for filename in os.listdir(characters_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(characters_dir, filename)
                character_id = filename[:-5]  # Retire l'extension .json
                with open(filepath, "r", encoding="utf-8") as file:
                    character_data = json.load(file)
                    state_data = character_data.get("state", {})
                    
                    # Skip characters that don't have all required fields
                    if not all(field in state_data for field in required_fields):
                        log_debug("Personnage ignoré (champs manquants)", action="get_all_characters", filename=filename, missing_fields=[field for field in required_fields if field not in state_data])
                        continue
                    
                    # L'ID est le nom du fichier (sans .json)
                    state_data["id"] = character_id
                    characters.append(Character(**state_data))
        log_debug("Chargement de tous les personnages", action="get_all_characters", count=len(characters))
        return characters

    @staticmethod
    def get_character(character_id: str) -> Character:
        """
        ### get_character
        **Description :** Récupère un personnage à partir de son identifiant (UUID) depuis le dossier data/characters.
        **Paramètres :**
        - `character_id` (str) : Identifiant du personnage (UUID).
        **Retour :** Objet Character (Pydantic).
        """       
        characters_dir = os.path.join(os.path.dirname(__file__), "../../data/characters")
        filepath = os.path.join(characters_dir, f"{character_id}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Le personnage {character_id} n'existe pas.")
        with open(filepath, "r", encoding="utf-8") as file:
            character_data = json.load(file)
            state_data = character_data.get("state", {})
            # L'ID est le nom du fichier (sans .json)
            state_data["id"] = character_id
            log_debug("Chargement du personnage", action="get_character", character_id=character_id)
            return Character(**state_data)

    @staticmethod
    def apply_xp(player_id: str, xp: int) -> dict:
        """
        ### apply_xp
        **Description :** Ajoute de l'XP à un personnage et persiste la fiche mise à jour.
        **Paramètres :**
        - `player_id` (str) : Identifiant du personnage (UUID).
        - `xp` (int) : Points d'expérience à ajouter.
        **Retour :**
        - (dict) : Fiche personnage mise à jour.
        """
        characters_dir = os.path.join(os.path.dirname(__file__), "../../data/characters")
        filepath = os.path.join(characters_dir, f"{player_id}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Le personnage {player_id} n'existe pas.")
        with open(filepath, "r", encoding="utf-8") as file:
            character_data = json.load(file)
        state = character_data.get("state", {})
        state["xp"] = state.get("xp", 0) + xp
        character_data["state"] = state
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(character_data, file, ensure_ascii=False, indent=2)
        log_debug("Ajout d'XP", action="apply_xp", player_id=player_id, xp_ajoute=xp, xp_total=state["xp"])
        return state

    @staticmethod
    def add_gold(player_id: str, gold: int) -> dict:
        """
        ### add_gold
        **Description :** Ajoute de l'or au portefeuille du personnage et persiste la fiche mise à jour.
        **Paramètres :**
        - `player_id` (str) : Identifiant du personnage (UUID).
        - `gold` (int) : Montant d'or à ajouter.
        **Retour :**
        - (dict) : Fiche personnage mise à jour.
        """
        characters_dir = os.path.join(os.path.dirname(__file__), "../../data/characters")
        filepath = os.path.join(characters_dir, f"{player_id}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Le personnage {player_id} n'existe pas.")
        with open(filepath, "r", encoding="utf-8") as file:
            character_data = json.load(file)
        state = character_data.get("state", {})
        state["gold"] = state.get("gold", 0) + gold
        character_data["state"] = state
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(character_data, file, ensure_ascii=False, indent=2)
        log_debug("Ajout d'or", action="add_gold", player_id=player_id, gold_ajoute=gold, gold_total=state["gold"])
        return state

    @staticmethod
    def take_damage(player_id: str, amount: int, source: str = "combat") -> dict:
        """
        ### take_damage
        **Description :** Diminue les points de vie d'un personnage et persiste la fiche mise à jour.
        **Paramètres :**
        - `player_id` (str) : Identifiant du personnage (UUID).
        - `amount` (int) : Points de dégâts à appliquer.
        - `source` (str) : Source des dégâts (optionnel).
        **Retour :**
        - (dict) : Fiche personnage mise à jour.
        """
        characters_dir = os.path.join(os.path.dirname(__file__), "../../data/characters")
        filepath = os.path.join(characters_dir, f"{player_id}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Le personnage {player_id} n'existe pas.")
        with open(filepath, "r", encoding="utf-8") as file:
            character_data = json.load(file)
        state = character_data.get("state", {})
        hp = state.get("hp", 100)
        state["hp"] = max(0, hp - amount)
        character_data["state"] = state
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(character_data, file, ensure_ascii=False, indent=2)
        log_debug("Application de dégâts", action="take_damage", player_id=player_id, amount=amount, hp_restant=state["hp"], source=source)
        return state
