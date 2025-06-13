"""
Tests pour le service de persistance de l'état du combat.
"""

import pytest
import json
import tempfile
import pathlib

from back.services.combat_state_service import CombatStateService
from back.models.domain.combat_state import CombatState


class TestCombatStateService:
    """
    ### TestCombatStateService
    **Description :** Tests pour le service de persistance de l'état du combat.
    """
    
    @pytest.fixture
    def temp_dir(self):
        """
        ### temp_dir
        **Description :** Fixture pour créer un répertoire temporaire.
        **Retour :** Répertoire temporaire.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            yield pathlib.Path(temp_dir)
    
    @pytest.fixture
    def service(self, temp_dir):
        """
        ### service
        **Description :** Fixture pour créer un service avec un répertoire temporaire.
        **Paramètres :**
        - `temp_dir` : Répertoire temporaire.
        **Retour :** Service de persistance configuré.
        """
        service = CombatStateService()
        service.data_dir = temp_dir / "combat"
        service.data_dir.mkdir(exist_ok=True, parents=True)
        return service
    
    @pytest.fixture
    def sample_combat_state(self):
        """
        ### sample_combat_state
        **Description :** Fixture pour créer un état de combat d'exemple.
        **Retour :** CombatState d'exemple.
        """
        participants = [
            {"id": "player1", "nom": "Héros", "hp": 50, "camp": "joueur"},
            {"id": "enemy1", "nom": "Orc", "hp": 30, "camp": "adversaire"}
        ]
        return CombatState(
            combat_id="test_combat_123",
            round=2,
            participants=participants,
            initiative_order=["player1", "enemy1"],
            current_turn=1,
            log=["Combat démarré", "Héros attaque"],
            status="en_cours"
        )
    
    def test_save_and_load_combat_state(self, service, sample_combat_state):
        """
        ### test_save_and_load_combat_state
        **Description :** Teste la sauvegarde et le chargement d'un état de combat.
        **Paramètres :**
        - `service` : Service de persistance.
        - `sample_combat_state` : État de combat d'exemple.
        """
        session_id = "test_session_123"
        
        # Sauvegarder
        service.save_combat_state(session_id, sample_combat_state)
        
        # Vérifier que le fichier existe
        file_path = service._get_combat_file_path(session_id)
        assert file_path.exists()
        
        # Charger et vérifier
        loaded_state = service.load_combat_state(session_id)
        assert loaded_state is not None
        assert loaded_state.combat_id == sample_combat_state.combat_id
        assert loaded_state.round == sample_combat_state.round
        assert loaded_state.status == sample_combat_state.status
        assert len(loaded_state.participants) == len(sample_combat_state.participants)
        assert loaded_state.initiative_order == sample_combat_state.initiative_order
    
    def test_load_nonexistent_combat_state(self, service):
        """
        ### test_load_nonexistent_combat_state
        **Description :** Teste le chargement d'un état de combat inexistant.
        **Paramètres :**
        - `service` : Service de persistance.
        """
        session_id = "inexistant"
        result = service.load_combat_state(session_id)
        assert result is None
    
    def test_delete_combat_state(self, service, sample_combat_state):
        """
        ### test_delete_combat_state
        **Description :** Teste la suppression d'un état de combat.
        **Paramètres :**
        - `service` : Service de persistance.
        - `sample_combat_state` : État de combat d'exemple.
        """
        session_id = "test_session_123"
        
        # Sauvegarder d'abord
        service.save_combat_state(session_id, sample_combat_state)
        file_path = service._get_combat_file_path(session_id)
        assert file_path.exists()
        
        # Supprimer
        service.delete_combat_state(session_id)
        assert not file_path.exists()
        
        # Vérifier que le chargement retourne None
        result = service.load_combat_state(session_id)
        assert result is None
    
    def test_delete_nonexistent_combat_state(self, service):
        """
        ### test_delete_nonexistent_combat_state
        **Description :** Teste la suppression d'un état de combat inexistant.
        **Paramètres :**
        - `service` : Service de persistance.
        """
        session_id = "inexistant"
        # Ne devrait pas lever d'exception
        service.delete_combat_state(session_id)
    
    def test_has_active_combat_true(self, service, sample_combat_state):
        """
        ### test_has_active_combat_true
        **Description :** Teste la détection d'un combat actif.
        **Paramètres :**
        - `service` : Service de persistance.
        - `sample_combat_state` : État de combat d'exemple.
        """
        session_id = "test_session_123"
        service.save_combat_state(session_id, sample_combat_state)
        
        assert service.has_active_combat(session_id) is True
    
    def test_has_active_combat_false_no_file(self, service):
        """
        ### test_has_active_combat_false_no_file
        **Description :** Teste la détection d'absence de combat (pas de fichier).
        **Paramètres :**
        - `service` : Service de persistance.
        """
        session_id = "inexistant"
        assert service.has_active_combat(session_id) is False
    
    def test_has_active_combat_false_terminated(self, service, sample_combat_state):
        """
        ### test_has_active_combat_false_terminated
        **Description :** Teste la détection d'absence de combat actif (combat terminé).
        **Paramètres :**
        - `service` : Service de persistance.
        - `sample_combat_state` : État de combat d'exemple.
        """
        session_id = "test_session_123"
        
        # Modifier l'état pour être terminé
        sample_combat_state.status = "termine"
        sample_combat_state.end_reason = "victoire"
        
        service.save_combat_state(session_id, sample_combat_state)
        
        assert service.has_active_combat(session_id) is False
    
    def test_save_combat_state_creates_directory(self, temp_dir, sample_combat_state):
        """
        ### test_save_combat_state_creates_directory
        **Description :** Teste que la sauvegarde crée le répertoire s'il n'existe pas.
        **Paramètres :**
        - `temp_dir` : Répertoire temporaire.
        - `sample_combat_state` : État de combat d'exemple.
        """
        # Créer un service sans créer le répertoire
        service = CombatStateService()
        service.data_dir = temp_dir / "new_combat_dir"
        
        session_id = "test_session_123"
        
        # Le répertoire ne devrait pas exister
        assert not service.data_dir.exists()
        
        # Sauvegarder devrait créer le répertoire
        service.save_combat_state(session_id, sample_combat_state)
        
        # Vérifier que le répertoire et le fichier existent
        assert service.data_dir.exists()
        file_path = service._get_combat_file_path(session_id)
        assert file_path.exists()
    
    def test_json_serialization_integrity(self, service, sample_combat_state):
        """
        ### test_json_serialization_integrity
        **Description :** Teste l'intégrité de la sérialisation JSON.
        **Paramètres :**
        - `service` : Service de persistance.
        - `sample_combat_state` : État de combat d'exemple.
        """
        session_id = "test_session_123"
        
        # Sauvegarder
        service.save_combat_state(session_id, sample_combat_state)
        
        # Lire directement le fichier JSON
        file_path = service._get_combat_file_path(session_id)
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        # Vérifier la structure
        assert "combat_id" in raw_data
        assert "round" in raw_data
        assert "participants" in raw_data
        assert "initiative_order" in raw_data
        assert "current_turn" in raw_data
        assert "log" in raw_data
        assert "status" in raw_data
        
        # Vérifier les valeurs
        assert raw_data["combat_id"] == sample_combat_state.combat_id
        assert raw_data["round"] == sample_combat_state.round
        assert raw_data["status"] == sample_combat_state.status
    
    def test_error_handling_invalid_json(self, service, temp_dir):
        """
        ### test_error_handling_invalid_json
        **Description :** Teste la gestion d'erreur avec un fichier JSON invalide.
        **Paramètres :**
        - `service` : Service de persistance.
        - `temp_dir` : Répertoire temporaire.
        """
        session_id = "test_session_123"
        file_path = service._get_combat_file_path(session_id)
        
        # Créer un fichier JSON invalide
        with open(file_path, 'w') as f:
            f.write("invalid json content")
        
        # Le chargement devrait retourner None sans lever d'exception
        result = service.load_combat_state(session_id)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
