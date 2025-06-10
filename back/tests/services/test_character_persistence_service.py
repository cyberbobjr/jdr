"""
Tests unitaires pour CharacterPersistenceService.
Validation de la factorisation du code de persistance des personnages.
"""

import pytest
from back.services.character_persistence_service import CharacterPersistenceService


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
        # Test avec un personnage existant
        assert CharacterPersistenceService.character_exists("79e55c14-7dd5-4189-b209-ea88f6d067eb") == True
        
        # Test avec un personnage inexistant
        assert CharacterPersistenceService.character_exists("non-existent-id") == False
    
    def test_load_character_data(self, isolated_data_dir):
        """
        ### test_load_character_data
        **Description :** Teste le chargement des données complètes d'un personnage.
        """
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        
        # Charger les données
        character_data = CharacterPersistenceService.load_character_data(character_id)
        
        # Vérifications
        assert isinstance(character_data, dict)
        assert "state" in character_data
        assert "created_at" in character_data
        assert character_data["state"]["name"] == "Galadhwen"
    
    def test_load_character_data_not_found(self):
        """
        ### test_load_character_data_not_found
        **Description :** Teste le chargement d'un personnage inexistant.
        """
        with pytest.raises(FileNotFoundError) as exc_info:
            CharacterPersistenceService.load_character_data("non-existent-id")
        
        assert "n'existe pas" in str(exc_info.value)
    
    def test_load_character_state(self, isolated_data_dir):
        """
        ### test_load_character_state
        **Description :** Teste le chargement de la section 'state' d'un personnage.
        """
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        
        # Charger l'état
        state = CharacterPersistenceService.load_character_state(character_id)
        
        # Vérifications
        assert isinstance(state, dict)
        assert state["name"] == "Galadhwen"
        assert "hp" in state
        assert "caracteristiques" in state
    
    def test_save_character_data(self, isolated_data_dir):
        """
        ### test_save_character_data
        **Description :** Teste la sauvegarde des données d'un personnage.
        """
        character_id = "test-character-id"
        test_data = {
            "state": {
                "name": "Test Character",
                "hp": 100,
                "xp": 50
            },
            "created_at": "2025-06-09T10:00:00",
            "last_update": "2025-06-09T10:00:00"
        }
        
        # Sauvegarder
        CharacterPersistenceService.save_character_data(character_id, test_data, "test")
        
        # Vérifier que le fichier existe
        assert CharacterPersistenceService.character_exists(character_id)
        
        # Recharger et vérifier
        loaded_data = CharacterPersistenceService.load_character_data(character_id)
        assert loaded_data["state"]["name"] == "Test Character"
        assert loaded_data["state"]["hp"] == 100
        assert loaded_data["state"]["xp"] == 50
    
    def test_update_character_state(self, isolated_data_dir):
        """
        ### test_update_character_state
        **Description :** Teste la mise à jour de la section 'state' d'un personnage.
        """
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        
        # Charger l'état initial
        initial_state = CharacterPersistenceService.load_character_state(character_id)
        initial_hp = initial_state.get("hp", 100)
        
        # Appliquer une mise à jour
        updates = {
            "hp": initial_hp - 10,
            "test_attribute": "test_value"
        }
        
        updated_state = CharacterPersistenceService.update_character_state(
            character_id, updates, "test")
        
        # Vérifications
        assert updated_state["hp"] == initial_hp - 10
        assert updated_state["test_attribute"] == "test_value"
        
        # Vérifier que les changements sont persistés
        reloaded_state = CharacterPersistenceService.load_character_state(character_id)
        assert reloaded_state["hp"] == initial_hp - 10
        assert reloaded_state["test_attribute"] == "test_value"
    
    def test_modify_character_attribute_addition(self, isolated_data_dir):
        """
        ### test_modify_character_attribute_addition
        **Description :** Teste la modification d'un attribut par addition.
        """
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        
        # Charger la valeur initiale
        initial_state = CharacterPersistenceService.load_character_state(character_id)
        initial_gold = initial_state.get("gold", 0)
        
        # Fonction de modification (ajout d'or)
        def add_gold(current_value):
            return current_value + 50
        
        # Appliquer la modification
        new_gold = CharacterPersistenceService.modify_character_attribute(
            character_id, "gold", add_gold, "add_gold")
        
        # Vérifications
        assert new_gold == initial_gold + 50
        
        # Vérifier la persistance
        updated_state = CharacterPersistenceService.load_character_state(character_id)
        assert updated_state["gold"] == initial_gold + 50
    
    def test_modify_character_attribute_damage(self, isolated_data_dir):
        """
        ### test_modify_character_attribute_damage
        **Description :** Teste la modification d'un attribut pour les dégâts (avec minimum).
        """
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        
        # Charger la valeur initiale
        initial_state = CharacterPersistenceService.load_character_state(character_id)
        initial_hp = initial_state.get("hp", 100)
        
        # Fonction de modification (dégâts avec minimum 0)
        def take_damage(current_hp):
            return max(0, current_hp - 30)
        
        # Appliquer la modification
        new_hp = CharacterPersistenceService.modify_character_attribute(
            character_id, "hp", take_damage, "take_damage")
        
        # Vérifications
        expected_hp = max(0, initial_hp - 30)
        assert new_hp == expected_hp
        
        # Vérifier la persistance
        updated_state = CharacterPersistenceService.load_character_state(character_id)
        assert updated_state["hp"] == expected_hp
    
    def test_modify_character_attribute_xp(self, isolated_data_dir):
        """
        ### test_modify_character_attribute_xp
        **Description :** Teste la modification d'un attribut pour l'XP.
        """
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        
        # Charger la valeur initiale
        initial_state = CharacterPersistenceService.load_character_state(character_id)
        initial_xp = initial_state.get("xp", 0)
        
        # Fonction de modification (ajout d'XP)
        def add_xp(current_xp):
            return current_xp + 100
        
        # Appliquer la modification
        new_xp = CharacterPersistenceService.modify_character_attribute(
            character_id, "xp", add_xp, "add_xp")
        
        # Vérifications
        assert new_xp == initial_xp + 100
        
        # Vérifier la persistance
        updated_state = CharacterPersistenceService.load_character_state(character_id)
        assert updated_state["xp"] == initial_xp + 100
    
    def test_modify_nonexistent_attribute(self, isolated_data_dir):
        """
        ### test_modify_nonexistent_attribute
        **Description :** Teste la modification d'un attribut qui n'existe pas encore.
        """
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        
        # Fonction de modification pour un nouvel attribut
        def set_new_attribute(current_value):
            return current_value + 42  # current_value sera 0 par défaut
        
        # Appliquer la modification
        new_value = CharacterPersistenceService.modify_character_attribute(
            character_id, "new_attribute", set_new_attribute, "set_new")
        
        # Vérifications
        assert new_value == 42
        
        # Vérifier la persistance
        updated_state = CharacterPersistenceService.load_character_state(character_id)
        assert updated_state["new_attribute"] == 42
