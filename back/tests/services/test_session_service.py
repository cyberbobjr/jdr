"""
Tests pour le service de session (sans dépendances complexes).
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from back.services.session_service import SessionService


class TestSessionService:
    """
    ### TestSessionService
    **Description :** Tests unitaires pour le service de session (simplifiés).
    """

    @pytest.fixture
    def temp_dir(self):
        """Crée un répertoire temporaire pour les tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    def test_session_service_initialization_with_mocks(self):
        """Test l'initialisation du service de session avec des mocks complets."""
        session_id = "test-session-123"
        
        # Mock pathlib pour éviter les accès au système de fichiers
        with patch("back.services.session_service.pathlib.Path") as mock_path:
            # Mock pour le project_root
            mock_project_root = MagicMock()
            mock_path.return_value = mock_project_root
            mock_project_root.parent.parent.parent = mock_project_root
            
            # Mock pour le chemin du store
            mock_history_path = mock_project_root / "data" / "sessions" / f"{session_id}.jsonl"
            mock_history_path.__str__ = MagicMock(return_value=f"/tmp/sessions/{session_id}.jsonl")
            
            # Mock PydanticJsonlStore
            with patch("back.services.session_service.PydanticJsonlStore") as mock_store:
                mock_store_instance = MagicMock()
                mock_store.return_value = mock_store_instance
                
                # Mock _load_session_data pour retourner False (pas de session existante)
                with patch.object(SessionService, "_load_session_data", return_value=False):
                    # Test avec parameters manquants (devrait lever une exception)
                    with pytest.raises(ValueError, match="n'existe pas"):
                        SessionService(session_id)

    def test_session_service_with_character_id_mock(self):
        """Test l'initialisation avec character_id en mockant les dépendances."""
        session_id = "test-session-456"
        character_id = "test-character"
        scenario_name = "test-scenario.md"
        
        with patch("back.services.session_service.pathlib.Path") as mock_path, \
             patch("back.services.session_service.PydanticJsonlStore") as mock_store, \
             patch.object(SessionService, "_load_session_data", return_value=False), \
             patch.object(SessionService, "_create_session") as mock_create:
            
            # Configuration des mocks
            mock_project_root = MagicMock()
            mock_path.return_value = mock_project_root
            mock_path.__file__ = "/test/session_service.py"
            mock_project_root.parent.parent.parent = mock_project_root
            
            mock_store_instance = MagicMock()
            mock_store.return_value = mock_store_instance
            
            # Créer la session
            session = SessionService(session_id, character_id, scenario_name)
            
            # Vérifications
            assert session.session_id == session_id
            assert session.character_id == character_id
            mock_create.assert_called_once_with(character_id, scenario_name)

    def test_session_service_store_initialization(self):
        """Test que le store est correctement initialisé."""
        session_id = "test-store-init"
        
        with patch("back.services.session_service.pathlib.Path") as mock_path, \
             patch("back.services.session_service.PydanticJsonlStore") as mock_store, \
             patch.object(SessionService, "_load_session_data", return_value=True):
            
            mock_project_root = MagicMock()
            mock_path.return_value = mock_project_root
            mock_path.__file__ = "/test/session_service.py"
            
            mock_store_instance = MagicMock()
            mock_store.return_value = mock_store_instance
            
            session = SessionService(session_id)
            
            assert session.store == mock_store_instance
            mock_store.assert_called_once()

    def test_session_service_absolute_path_handling(self):
        """Test le traitement des chemins absolus pour session_id."""
        absolute_session_id = "/tmp/absolute/session"
        
        with patch("back.services.session_service.os.path.isabs", return_value=True), \
             patch("back.services.session_service.PydanticJsonlStore") as mock_store, \
             patch.object(SessionService, "_load_session_data", return_value=True):
            
            mock_store_instance = MagicMock()
            mock_store.return_value = mock_store_instance
            
            session = SessionService(absolute_session_id)
            
            # Vérifier que le store est appelé avec le bon chemin
            expected_path = absolute_session_id + ".jsonl"
            mock_store.assert_called_once_with(expected_path)

    def test_session_attributes_initialization(self):
        """Test que tous les attributs sont correctement initialisés."""
        session_id = "test-attributes"
        
        with patch("back.services.session_service.pathlib.Path"), \
             patch("back.services.session_service.PydanticJsonlStore"), \
             patch.object(SessionService, "_load_session_data", return_value=True):
            
            session = SessionService(session_id)
            
            # Vérifier que tous les attributs sont initialisés
            assert session.session_id == session_id
            assert session.character_id is None  # Initial value
            assert isinstance(session.character_data, dict)
            assert session.scenario_name == ""  # Initial value
            assert session.character_service is None  # Initial value
            assert session.store is not None
