"""
Tests unitaires pour la gestion des statuts de personnages dans CharacterService
"""
import os
import json
import tempfile
from unittest.mock import patch
from back.services.character_service import CharacterService


class TestCharacterServiceStatus:
    """
    Tests pour la gestion automatique des statuts des personnages
    """
    
    def setup_method(self):
        """Configuration avant chaque test"""
        self.temp_dir = tempfile.mkdtemp()
        self.characters_dir = os.path.join(self.temp_dir, "characters")
        os.makedirs(self.characters_dir, exist_ok=True)
    
    def teardown_method(self):
        """Nettoyage après chaque test"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_character_file(self, character_id: str, character_data: dict):
        """Crée un fichier de personnage de test"""
        filepath = os.path.join(self.characters_dir, f"{character_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(character_data, f, ensure_ascii=False, indent=2)
        return filepath
    
    @patch('back.services.character_service.os.listdir')
    @patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data')
    def test_get_all_characters_sets_status_en_cours_for_incomplete_characters(self, mock_load_character_data, mock_listdir):
        """
        Test que get_all_characters() définit le statut à "en_cours" pour les personnages incomplets
        """
        # Simuler la présence d'un fichier de personnage
        mock_listdir.return_value = ["test-id-1.json"]
        
        # Créer un personnage incomplet (name = null)
        incomplete_character = {
            "id": "test-id-1",
            "status": None,
            "name": None,
            "race": {"name": "Humain", "characteristic_bonuses": {}, "destiny_points": 1, "special_abilities": [], "base_languages": [], "optional_languages": []},
            "culture": {"name": "Gondor", "description": ""},
            "caracteristiques": {"Force": 50},
            "competences": {"Combat": 10},
            "hp": 100,
            "inventory": [],
            "spells": []
        }
        
        mock_load_character_data.return_value = incomplete_character
        
        # Appeler la méthode
        characters = CharacterService.get_all_characters()
        
        # Vérifications
        assert len(characters) == 1
        character = characters[0]
        assert isinstance(character, dict)
        assert character["status"] == "en_cours"
        assert character["id"] == "test-id-1"
    
    @patch('back.services.character_service.os.listdir')
    @patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data')
    def test_get_all_characters_sets_status_complet_for_complete_characters(self, mock_load_character_data, mock_listdir):
        """
        Test que get_all_characters() définit le statut à "complet" pour les personnages complets
        """
        # Simuler la présence d'un fichier de personnage
        mock_listdir.return_value = ["test-id-2.json"]
        
        # Créer un personnage complet
        complete_character = {
            "id": "test-id-2",
            "status": None,
            "name": "Aragorn",
            
            "race": {"name": "Humain", "characteristic_bonuses": {}, "destiny_points": 1, "special_abilities": [], "base_languages": [], "optional_languages": []},
            "culture": {"name": "Gondor", "description": ""},
            "caracteristiques": {"Force": 50, "Constitution": 50, "Agilité": 50, "Rapidité": 50, "Volonté": 50, "Raisonnement": 50, "Intuition": 50, "Présence": 50},
            "competences": {"Combat": 10},
            "hp": 100,
            "inventory": [],
            "spells": []
        }
        
        mock_load_character_data.return_value = complete_character
        
        # Appeler la méthode
        characters = CharacterService.get_all_characters()
        
        # Vérifications
        assert len(characters) == 1
        character = characters[0]
        # Le personnage complet doit être retourné comme un objet Character (pas un dict)
        # mais on vérifie le statut dans les données
        if hasattr(character, 'model_dump'):
            character_data = character.model_dump()
        else:
            character_data = character
        assert character_data["status"] == "complet"
    
    @patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data')
    def test_get_character_sets_status_en_cours_for_incomplete_character(self, mock_load_character_data):
        """
        Test que get_character() définit le statut à "en_cours" pour un personnage incomplet
        """
        # Données de personnage incomplet
        incomplete_data = {
            "name": None,
            "race": {"name": "Elfe", "characteristic_bonuses": {}, "destiny_points": 2, "special_abilities": [], "base_languages": [], "optional_languages": []},
            "culture": {"name": "Sindar", "description": ""},
            "caracteristiques": {"Force": 50},
            "competences": {"Combat": 10},
            "hp": 100,
            "inventory": [],
            "spells": []
        }
        
        mock_load_character_data.return_value = incomplete_data
          # Appeler la méthode
        result = CharacterService.get_character_by_id("test-id")
        
        # Vérifications
        assert result["status"] == "en_cours"
        assert result["id"] == "test-id"
    
    @patch('back.services.character_persistence_service.CharacterPersistenceService.load_character_data')
    def test_get_character_sets_status_complet_for_complete_character(self, mock_load_character_data):
        """
        Test que get_character() définit le statut à "complet" pour un personnage complet
        """
        # Données de personnage complet
        complete_data = {
            "name": "Legolas",
            
            "status": None,  # On veut que le système le détecte comme complet
            "race": {"name": "Elfe", "characteristic_bonuses": {}, "destiny_points": 2, "special_abilities": [], "base_languages": [], "optional_languages": []},
            "culture": {"name": "Sindar", "description": ""},
            "caracteristiques": {"Force": 50, "Constitution": 50, "Agilité": 50, "Rapidité": 50, "Volonté": 50, "Raisonnement": 50, "Intuition": 50, "Présence": 50},
            "competences": {"Combat": 10},
            "hp": 100,
            "inventory": [],
            "spells": []
        }
        
        mock_load_character_data.return_value = complete_data
        
        # Appeler la méthode
        result = CharacterService.get_character_by_id("test-id")
        
        # Vérifications
        assert result["status"] == "complet"
        assert result["id"] == "test-id"
        assert result["name"] == "Legolas"
