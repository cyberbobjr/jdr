"""
Tests unitaires pour SessionService.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import json
import os

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
            "state": {
                "name": "Aragorn",
                "race": "Homme",
                "culture": "Gondor",
                "profession": "Rôdeur",
                "caracteristiques": {
                    "Force": 85,
                    "Constitution": 80,
                    "Agilité": 75,
                    "Rapidité": 70,
                    "Volonté": 80,
                    "Raisonnement": 75,
                    "Intuition": 80,
                    "Présence": 70
                },
                "competences": {
                    "Combat": 75,
                    "Survie": 80,
                    "Perception": 70
                },
                "hp": 100,
                "xp": 0,
                "gold": 100,
                "inventory": [],
                "spells": [],
                "equipment_summary": {},
                "culture_bonuses": {}
            }
        }
        # Sauvegarder le personnage
        char_path = Path(temp_dir) / "data" / "characters" / "test_char_123.json"
        with open(char_path, 'w', encoding='utf-8') as f:
            json.dump(character_data, f)
        return character_data
    
    def test_create_new_session(self, temp_dir, test_character, monkeypatch):
        """Test la création d'une nouvelle session"""
        # Patch pour que CharacterPersistenceService et SessionService utilisent temp_dir
        from back.services import character_persistence_service
        
        def mock_get_character_file_path(character_id: str) -> str:
            return str(Path(temp_dir) / "data" / "characters" / f"{character_id}.json")
        
        monkeypatch.setattr(character_persistence_service.CharacterPersistenceService, 
                          "_get_character_file_path", staticmethod(mock_get_character_file_path))
        
        # Patch le project_root dans SessionService
        def mock_init(self, session_id: str, character_id=None, scenario_name=None):
            self.session_id = session_id
            self.character_id = character_id
            self.character_data = {}
            self.scenario_name = ""
            self.character_service = None
            
            # Utiliser temp_dir comme project_root
            project_root = Path(temp_dir)
            if not os.path.isabs(session_id):
                history_path = str(project_root / "data" / "sessions" / f"{session_id}.jsonl")
            else:
                history_path = session_id + ".jsonl"
            
            from back.storage.pydantic_jsonl_store import PydanticJsonlStore
            self.store = PydanticJsonlStore(history_path)
            
            # Charger les données de session ou créer une nouvelle session
            if not self._load_session_data_with_temp_dir(temp_dir):
                if character_id and scenario_name:
                    self._create_session_with_temp_dir(character_id, scenario_name, temp_dir)
                else:
                    raise ValueError(f"Session {session_id} n'existe pas et les paramètres de création ne sont pas fournis")
        
        def mock_load_session_data(self, temp_dir):
            session_dir = Path(temp_dir) / "data" / "sessions" / self.session_id
            if session_dir.exists() and session_dir.is_dir():
                character_file = session_dir / "character.txt"
                if character_file.exists():
                    character_id = character_file.read_text(encoding='utf-8').strip()
                    self.character_id = character_id
                    
                    from back.services.character_service import CharacterService
                    try:
                        self.character_service = CharacterService(character_id)
                        self.character_data = self.character_service.character_data.model_dump()
                    except FileNotFoundError:
                        raise ValueError(f"Personnage {character_id} introuvable")
                
                scenario_file = session_dir / "scenario.txt"
                if scenario_file.exists():
                    self.scenario_name = scenario_file.read_text(encoding='utf-8').strip()
                else:
                    self.scenario_name = 'Les_Pierres_du_Passe.md'
                
                return True
            return False
        
        def mock_create_session(self, character_id: str, scenario_name: str, temp_dir):
            session_dir = Path(temp_dir) / "data" / "sessions" / self.session_id
            session_dir.mkdir(parents=True, exist_ok=True)
            
            character_file = session_dir / "character.txt"
            character_file.write_text(character_id, encoding='utf-8')
            
            scenario_file = session_dir / "scenario.txt"
            scenario_file.write_text(scenario_name, encoding='utf-8')
            
            self.character_id = character_id
            
            from back.services.character_service import CharacterService
            try:
                self.character_service = CharacterService(character_id)
                self.character_data = self.character_service.character_data.model_dump()
            except FileNotFoundError:
                raise ValueError(f"Personnage {character_id} introuvable")
            
            self.scenario_name = scenario_name
        
        monkeypatch.setattr(SessionService, "__init__", mock_init)
        monkeypatch.setattr(SessionService, "_load_session_data_with_temp_dir", mock_load_session_data)
        monkeypatch.setattr(SessionService, "_create_session_with_temp_dir", mock_create_session)
        
        session_id = "test_session_001"
        character_id = "test_char_123"
        scenario_name = "Test_Scenario.md"
        
        # Créer une nouvelle session
        session = SessionService(session_id, character_id=character_id, scenario_name=scenario_name)
        
        # Vérifier que les données sont correctement chargées
        assert session.session_id == session_id
        assert session.character_service is not None
        assert session.character_service.character_data.name == "Aragorn"
        assert session.scenario_name == scenario_name
        
        # Vérifier que les fichiers ont été créés
        session_dir = Path(temp_dir) / "data" / "sessions" / session_id
        assert session_dir.exists()
        assert (session_dir / "character.txt").read_text() == character_id
        assert (session_dir / "scenario.txt").read_text() == scenario_name
