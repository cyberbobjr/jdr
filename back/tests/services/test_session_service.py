"""
Tests unitaires pour SessionService.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import json

from back.services.session_service import SessionService


class TestSessionService:
    """Tests pour SessionService"""
    
    @pytest.fixture
    def temp_dir(self):
        """Crée un répertoire temporaire pour les tests"""
        temp_dir = tempfile.mkdtemp()
        # Créer la structure de données attendue
        data_dir = Path(temp_dir) / "data"
        data_dir.mkdir()
        (data_dir / "sessions").mkdir()
        (data_dir / "characters").mkdir()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def test_character(self, temp_dir):
        """Crée un personnage de test"""
        character_data = {
            "id": "test_char_123",
            "name": "Aragorn",
            "class": "Rôdeur",
            "level": 5
        }
        # Sauvegarder le personnage
        char_path = Path(temp_dir) / "data" / "characters" / "test_char_123.json"
        with open(char_path, 'w', encoding='utf-8') as f:
            json.dump(character_data, f)
        return character_data
    
    def test_create_new_session(self, temp_dir, test_character, monkeypatch):
        """Test la création d'une nouvelle session"""
        # Monkeypatch pour que SessionService utilise notre temp_dir
        monkeypatch.setattr(Path, "__new__", lambda cls, *args: Path(temp_dir) if len(args) == 1 and args[0] == __file__ else Path(*args))
        
        session_id = "test_session_001"
        character_id = "test_char_123"
        scenario_name = "Test_Scenario.md"
        
        # Créer une nouvelle session
        session = SessionService(session_id, character_id=character_id, scenario_name=scenario_name)
        
        # Vérifier que les données sont correctement chargées
        assert session.session_id == session_id
        assert session.character_data["name"] == "Aragorn"
        assert session.scenario_name == scenario_name
        
        # Vérifier que les fichiers ont été créés
        session_dir = Path(temp_dir) / "data" / "sessions" / session_id
        assert session_dir.exists()
        assert (session_dir / "character.txt").read_text() == character_id
        assert (session_dir / "scenario.txt").read_text() == scenario_name
    
    def test_load_existing_session(self, temp_dir, test_character, monkeypatch):
        """Test le chargement d'une session existante"""
        monkeypatch.setattr(Path, "__new__", lambda cls, *args: Path(temp_dir) if len(args) == 1 and args[0] == __file__ else Path(*args))
        
        session_id = "existing_session"
        character_id = "test_char_123"
        scenario_name = "Existing_Scenario.md"
        
        # Créer manuellement les fichiers de session
        session_dir = Path(temp_dir) / "data" / "sessions" / session_id
        session_dir.mkdir(parents=True)
        (session_dir / "character.txt").write_text(character_id)
        (session_dir / "scenario.txt").write_text(scenario_name)
        
        # Charger la session
        session = SessionService(session_id)
        
        # Vérifier que les données sont correctement chargées
        assert session.character_data["name"] == "Aragorn"
        assert session.scenario_name == scenario_name
    
    def test_session_not_found_error(self, temp_dir, monkeypatch):
        """Test l'erreur quand une session n'existe pas"""
        monkeypatch.setattr(Path, "__new__", lambda cls, *args: Path(temp_dir) if len(args) == 1 and args[0] == __file__ else Path(*args))
        
        with pytest.raises(ValueError, match="n'existe pas"):
            SessionService("non_existent_session")
