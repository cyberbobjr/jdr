from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from back.app import app
from back.models.domain.combat_state import CombatState

client = TestClient(app)


class TestCombatRouter:
    """Tests pour le routeur de combat."""

    @patch('back.routers.combat.CombatService')
    def test_attack_endpoint_success(self, mock_combat_service_class):
        """
        ### test_attack_endpoint_success
        **Description:** Teste l'endpoint d'attaque avec succès.
        **Paramètres:** Aucun.
        **Retour:** Aucun.
        """
        # Arrange
        mock_service = MagicMock()
        mock_combat_service_class.return_value = mock_service
        
        # Mock du combat state de retour
        mock_combat_state = MagicMock(spec=CombatState)
        mock_combat_state.to_dict.return_value = {
            "combat_id": "test_combat",
            "status": "en_cours",
            "participants": [
                {"id": "attacker", "hp": 20},
                {"id": "target", "hp": 15}
            ]
        }
        
        mock_service.perform_attack.return_value = mock_combat_state
        
        # Act
        response = client.post("/api/combat/attack", params={
            "attacker_id": "attacker",
            "target_id": "target", 
            "attack_value": 75,
            "combat_state": '{"combat_id": "test_combat", "status": "en_cours"}'
        })
        
        # Assert
        assert response.status_code == 200
        assert "combat_id" in response.json()
        assert "participants" in response.json()

    @patch('back.routers.combat.CombatService')
    def test_attack_endpoint_validation_error(self, mock_combat_service_class):
        """
        ### test_attack_endpoint_validation_error
        **Description:** Teste l'endpoint d'attaque avec des paramètres invalides.
        **Paramètres:** Aucun.
        **Retour:** Aucun.
        """
        # Act - Appel sans paramètres requis
        response = client.post("/api/combat/attack")
        
        # Assert
        assert response.status_code == 422  # Unprocessable Entity

    @patch('back.routers.combat.CombatService')
    def test_attack_endpoint_service_error(self, mock_combat_service_class):
        """
        ### test_attack_endpoint_service_error
        **Description:** Teste la gestion d'erreur du service de combat.
        **Paramètres:** Aucun.
        **Retour:** Aucun.
        """
        # Arrange
        mock_service = MagicMock()
        mock_combat_service_class.return_value = mock_service
        mock_service.perform_attack.side_effect = Exception("Combat error")
        
        # Act
        response = client.post("/api/combat/attack", params={
            "attacker_id": "attacker",
            "target_id": "target",
            "attack_value": 75,
            "combat_state": '{"combat_id": "test_combat"}'
        })
        
        # Assert
        assert response.status_code == 500

    @patch('back.routers.combat.log_debug')
    @patch('back.routers.combat.CombatService')
    def test_attack_endpoint_logs_debug(self, mock_combat_service_class, mock_log_debug):
        """
        ### test_attack_endpoint_logs_debug
        **Description:** Vérifie que les logs de debug sont correctement appelés.
        **Paramètres:** Aucun.
        **Retour:** Aucun.
        """
        # Arrange
        mock_service = MagicMock()
        mock_combat_service_class.return_value = mock_service
        
        mock_combat_state = MagicMock(spec=CombatState)
        mock_combat_state.to_dict.return_value = {"combat_id": "test"}
        mock_service.perform_attack.return_value = mock_combat_state
        
        # Act
        response = client.post("/api/combat/attack", params={
            "attacker_id": "attacker",
            "target_id": "target",
            "attack_value": 75,
            "combat_state": '{"combat_id": "test_combat"}'
        })
        
        # Assert
        mock_log_debug.assert_called()
