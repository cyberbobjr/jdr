"""
Tests unitaires pour CharacterPersistenceService.
Validation de la factorisation du code de persistance des personnages.
"""

import pytest
from back.services.character_persistence_service import CharacterPersistenceService
from unittest.mock import patch
import json


class TestCharacterPersistenceService:
    """
    ### TestCharacterPersistenceService
    **Description :** Tests unitaires pour le service de persistance centralisé des personnages.
    """
    
    def test_character_exists(self, isolated_data_dir):
        """
        ### test_character_exists
        **Description :** Teste la vérification d'existence d'un personnage.
        """
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        characters_dir = isolated_data_dir / "characters"
        characters_dir.mkdir(exist_ok=True)
        # Création d'un fichier personnage minimal
        (characters_dir / f"{character_id}.json").write_text(json.dumps({"name": "Galadhwen", "hp": 42, "caracteristiques": {}}), encoding="utf-8")
        with patch("back.services.character_persistence_service.get_data_dir", return_value=str(isolated_data_dir)):
            assert CharacterPersistenceService.character_exists(character_id) is True
            assert CharacterPersistenceService.character_exists("non-existent-id") is False
    
    def test_load_character_data(self, isolated_data_dir):
        """
        ### test_load_character_data
        **Description :** Teste le chargement des données complètes d'un personnage.
        """
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        characters_dir = isolated_data_dir / "characters"
        characters_dir.mkdir(exist_ok=True)
        (characters_dir / f"{character_id}.json").write_text(json.dumps({"name": "Galadhwen", "hp": 42, "caracteristiques": {}}), encoding="utf-8")
        with patch("back.services.character_persistence_service.get_data_dir", return_value=str(isolated_data_dir)):
            character_data = CharacterPersistenceService.load_character_data(character_id)

            # Vérifications
            assert isinstance(character_data, dict)
            assert "name" in character_data
            # 'created_at' est optionnel, donc on ne l'exige pas
    
    def test_load_character_data_not_found(self, isolated_data_dir):
        """
        ### test_load_character_data_not_found
        **Description :** Teste le chargement d'un personnage inexistant.
        """
        with patch("back.services.character_persistence_service.get_data_dir", return_value=str(isolated_data_dir)):
            with pytest.raises(FileNotFoundError) as exc_info:
                CharacterPersistenceService.load_character_data("non-existent-id")
            assert "n'existe pas" in str(exc_info.value)

    def test_save_character_data(self, isolated_data_dir):
        """
        ### test_save_character_data
        **Description :** Teste la sauvegarde des données d'un personnage.
        """
        character_id = "test-character-id"
        test_data = {
            "name": "Test Character",
            "hp": 100,
            "xp": 50,
            "created_at": "2025-06-09T10:00:00",
            "last_update": "2025-06-09T10:00:00"
        }
        
        # Sauvegarder
        CharacterPersistenceService.save_character_data(character_id, test_data)
        
        # Vérifier que le fichier existe
        assert CharacterPersistenceService.character_exists(character_id)
        
        # Recharger et vérifier
        loaded_data = CharacterPersistenceService.load_character_data(character_id)
        assert loaded_data["name"] == "Test Character"
        assert loaded_data["hp"] == 100
        assert loaded_data["xp"] == 50
