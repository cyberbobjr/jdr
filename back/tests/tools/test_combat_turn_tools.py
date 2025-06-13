"""
Tests pour les nouveaux outils de gestion des tours de combat.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from back.tools.combat_tools import (
    end_turn_tool, check_combat_end_tool, apply_damage_tool, 
    get_combat_status_tool, start_combat_tool
)
from back.models.domain.combat_state import CombatState


class TestCombatTurnTools:
    """
    ### TestCombatTurnTools
    **Description :** Tests pour les nouveaux outils de gestion des tours de combat.
    """
    
    @pytest.fixture
    def mock_session_service(self):
        """
        ### mock_session_service
        **Description :** Fixture pour simuler SessionService.
        **Retour :** Mock de SessionService.
        """
        mock_service = Mock()
        mock_service.session_id = "test_session_123"
        return mock_service
    
    @pytest.fixture
    def mock_context(self, mock_session_service):
        """
        ### mock_context
        **Description :** Fixture pour simuler RunContext.
        **Paramètres :**
        - `mock_session_service` : Service de session simulé.
        **Retour :** Mock de RunContext.
        """
        mock_ctx = Mock()
        mock_ctx.deps = mock_session_service
        return mock_ctx
    
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
            round=1,
            participants=participants,
            initiative_order=["player1", "enemy1"],
            current_turn=0,
            log=["Combat démarré"],
            status="en_cours"
        )
    
    def test_start_combat_tool_success(self, mock_context):
        """
        ### test_start_combat_tool_success
        **Description :** Teste le démarrage réussi d'un combat.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        participants = [
            {"nom": "Héros", "hp": 50, "camp": "joueur"},
            {"nom": "Orc", "hp": 30, "camp": "adversaire"}
        ]
        
        with patch('back.tools.combat_tools.combat_state_service') as mock_state_service, \
             patch('back.tools.combat_tools.combat_service') as mock_combat_service:
            
            mock_state_service.has_active_combat.return_value = False
            mock_combat_service.start_combat.return_value = MagicMock()
            mock_combat_service.roll_initiative.return_value = MagicMock()
            mock_combat_service.get_combat_summary.return_value = {"status": "en_cours"}
            
            result = start_combat_tool(mock_context, participants)
            
            assert isinstance(result, dict)
            mock_state_service.save_combat_state.assert_called_once()
    
    def test_start_combat_tool_already_active(self, mock_context):
        """
        ### test_start_combat_tool_already_active
        **Description :** Teste le démarrage d'un combat quand un autre est déjà actif.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        participants = [{"nom": "Héros", "hp": 50}]
        
        with patch('back.tools.combat_tools.combat_state_service') as mock_state_service:
            mock_state_service.has_active_combat.return_value = True
            
            result = start_combat_tool(mock_context, participants)
            
            assert "error" in result
            assert "déjà en cours" in result["error"]
    
    def test_end_turn_tool_success(self, mock_context, sample_combat_state):
        """
        ### test_end_turn_tool_success
        **Description :** Teste la fin de tour réussie.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        - `sample_combat_state` : État de combat d'exemple.
        """
        combat_id = "test_combat_123"
        
        with patch('back.tools.combat_tools.combat_state_service') as mock_state_service, \
             patch('back.tools.combat_tools.combat_service') as mock_combat_service:
            
            mock_state_service.load_combat_state.return_value = sample_combat_state
            mock_combat_service.end_turn.return_value = sample_combat_state
            mock_combat_service.get_combat_summary.return_value = {"round": 1}
            
            result = end_turn_tool(mock_context, combat_id)
            
            assert isinstance(result, dict)
            assert "message" in result
            mock_state_service.save_combat_state.assert_called_once()
    
    def test_end_turn_tool_combat_not_found(self, mock_context):
        """
        ### test_end_turn_tool_combat_not_found
        **Description :** Teste la fin de tour quand le combat n'existe pas.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        combat_id = "inexistant"
        
        with patch('back.tools.combat_tools.combat_state_service') as mock_state_service:
            mock_state_service.load_combat_state.return_value = None
            
            result = end_turn_tool(mock_context, combat_id)
            
            assert "error" in result
            assert "non trouvé" in result["error"]
    
    def test_check_combat_end_tool_continuing(self, mock_context, sample_combat_state):
        """
        ### test_check_combat_end_tool_continuing
        **Description :** Teste la vérification de fin quand le combat continue.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        - `sample_combat_state` : État de combat d'exemple.
        """
        combat_id = "test_combat_123"
        
        with patch('back.tools.combat_tools.combat_state_service') as mock_state_service, \
             patch('back.tools.combat_tools.combat_service') as mock_combat_service:
            
            mock_state_service.load_combat_state.return_value = sample_combat_state
            mock_combat_service.check_combat_end.return_value = False
            
            result = check_combat_end_tool(mock_context, combat_id)
            
            assert result["combat_ended"] is False
            assert result["status"] == "en_cours"
    
    def test_check_combat_end_tool_ended(self, mock_context, sample_combat_state):
        """
        ### test_check_combat_end_tool_ended
        **Description :** Teste la vérification de fin quand le combat est terminé.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        - `sample_combat_state` : État de combat d'exemple.
        """
        combat_id = "test_combat_123"
        
        # Modifier l'état pour que tous les ennemis soient morts
        sample_combat_state.participants[1]["hp"] = 0
        
        with patch('back.tools.combat_tools.combat_state_service') as mock_state_service, \
             patch('back.tools.combat_tools.combat_service') as mock_combat_service:
            
            mock_state_service.load_combat_state.return_value = sample_combat_state
            mock_combat_service.check_combat_end.return_value = True
            mock_combat_service.end_combat.return_value = sample_combat_state
            mock_combat_service.get_combat_summary.return_value = {"status": "termine"}
            
            result = check_combat_end_tool(mock_context, combat_id)
            
            assert result["combat_ended"] is True
            assert result["end_reason"] == "victoire"
            mock_state_service.delete_combat_state.assert_called_once()
    
    def test_apply_damage_tool_success(self, mock_context, sample_combat_state):
        """
        ### test_apply_damage_tool_success
        **Description :** Teste l'application de dégâts réussie.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        - `sample_combat_state` : État de combat d'exemple.
        """
        combat_id = "test_combat_123"
        target_id = "enemy1"
        damage = 10
        
        with patch('back.tools.combat_tools.combat_state_service') as mock_state_service, \
             patch('back.tools.combat_tools.combat_service') as mock_combat_service:
            
            mock_state_service.load_combat_state.return_value = sample_combat_state
            mock_combat_service.apply_damage.return_value = sample_combat_state
            mock_combat_service.check_combat_end.return_value = False
            mock_combat_service.get_combat_summary.return_value = {"round": 1}
            
            result = apply_damage_tool(mock_context, combat_id, target_id, damage)
            
            assert result["damage_applied"] == damage
            assert "target" in result
            mock_state_service.save_combat_state.assert_called_once()
    
    def test_apply_damage_tool_ends_combat(self, mock_context, sample_combat_state):
        """
        ### test_apply_damage_tool_ends_combat
        **Description :** Teste l'application de dégâts qui termine le combat.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        - `sample_combat_state` : État de combat d'exemple.
        """
        combat_id = "test_combat_123"
        target_id = "enemy1"
        damage = 30  # Dégâts mortels
        
        with patch('back.tools.combat_tools.combat_state_service') as mock_state_service, \
             patch('back.tools.combat_tools.combat_service') as mock_combat_service:
            
            # Simuler la mort de l'ennemi
            dead_state = sample_combat_state.model_copy()
            dead_state.participants[1]["hp"] = 0
            
            mock_state_service.load_combat_state.return_value = sample_combat_state
            mock_combat_service.apply_damage.return_value = dead_state
            mock_combat_service.check_combat_end.return_value = True
            mock_combat_service.end_combat.return_value = dead_state
            mock_combat_service.get_combat_summary.return_value = {"status": "termine"}
            
            result = apply_damage_tool(mock_context, combat_id, target_id, damage)
            
            assert result["damage_applied"] == damage
            assert "auto_ended" in result
            assert result["auto_ended"]["reason"] == "victoire"
            mock_state_service.delete_combat_state.assert_called_once()
    
    def test_get_combat_status_tool_success(self, mock_context, sample_combat_state):
        """
        ### test_get_combat_status_tool_success
        **Description :** Teste la récupération du statut de combat.
        **Paramètres :**
        - `mock_context` : Contexte d'exécution simulé.
        - `sample_combat_state` : État de combat d'exemple.
        """
        combat_id = "test_combat_123"
        
        with patch('back.tools.combat_tools.combat_state_service') as mock_state_service, \
             patch('back.tools.combat_tools.combat_service') as mock_combat_service:
            
            mock_state_service.load_combat_state.return_value = sample_combat_state
            mock_combat_service.get_combat_summary.return_value = {"round": 1}
            
            result = get_combat_status_tool(mock_context, combat_id)
            
            assert isinstance(result, dict)
            assert "current_participant" in result
            assert "alive_participants" in result
            assert "dead_participants" in result


if __name__ == "__main__":
    pytest.main([__file__])
