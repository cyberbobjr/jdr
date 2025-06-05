from unittest.mock import patch
from back.services.skill_service import perform_skill_check_with_character


class TestSkillService:
    """Tests pour le service de compétences."""

    @patch('back.services.skill_service.skill_check_with_character')
    def test_perform_skill_check_with_character_basic(self, mock_skill_check):
        """
        ### test_perform_skill_check_with_character_basic
        **Description:** Teste l'exécution d'un test de compétence basique avec un personnage.
        **Paramètres:** Aucun.
        **Retour:** Aucun.
        """
        # Arrange
        mock_skill_check.return_value = "Test de Perception: Compétence Perception = 75, Jet 1d100 = 45, Seuil = 75 (75 - 0), Résultat: **Réussite Simple**"
        
        skill_name = "Perception"
        character_json = '{"competences": {"Perception": 75}, "caracteristiques": {"Intuition": 65}}'
        difficulty_name = "Moyenne"
        difficulty_modifier = 0
        
        # Act
        result = perform_skill_check_with_character(skill_name, character_json, difficulty_name, difficulty_modifier)
        
        # Assert
        assert "Perception" in result
        assert "Réussite" in result or "Échec" in result
        mock_skill_check.assert_called_once_with(
            skill_name=skill_name,
            character_json=character_json,
            difficulty_name=difficulty_name,
            difficulty_modifier=difficulty_modifier
        )

    @patch('back.services.skill_service.skill_check_with_character')
    def test_perform_skill_check_with_character_different_difficulty(self, mock_skill_check):
        """
        ### test_perform_skill_check_with_character_different_difficulty
        **Description:** Teste l'exécution d'un test de compétence avec différents niveaux de difficulté.
        **Paramètres:** Aucun.
        **Retour:** Aucun.
        """
        # Arrange
        mock_skill_check.return_value = "Test de Force: Caractéristique Force = 80, Jet 1d100 = 95, Seuil = 60 (80 - 20), Résultat: **Échec Simple**"
        
        skill_name = "Force"
        character_json = '{"caracteristiques": {"Force": 80}}'
        difficulty_name = "Difficile"
        difficulty_modifier = 0
        
        # Act
        result = perform_skill_check_with_character(skill_name, character_json, difficulty_name, difficulty_modifier)
        
        # Assert
        assert "Force" in result
        assert "Échec" in result or "Réussite" in result
        mock_skill_check.assert_called_once_with(
            skill_name=skill_name,
            character_json=character_json,
            difficulty_name=difficulty_name,
            difficulty_modifier=difficulty_modifier
        )

    @patch('back.services.skill_service.skill_check_with_character')
    def test_perform_skill_check_with_character_with_modifier(self, mock_skill_check):
        """
        ### test_perform_skill_check_with_character_with_modifier
        **Description:** Teste l'exécution d'un test de compétence avec un modificateur de difficulté.
        **Paramètres:** Aucun.
        **Retour:** Aucun.
        """
        # Arrange
        mock_skill_check.return_value = "Test de Discrétion: Compétence Discrétion = 60, Jet 1d100 = 25, Seuil = 50 (60 - 10), Résultat: **Réussite Bonne**"
        
        skill_name = "Discrétion"
        character_json = '{"competences": {"Discrétion": 60}}'
        difficulty_name = "Moyenne"
        difficulty_modifier = 10
        
        # Act
        result = perform_skill_check_with_character(skill_name, character_json, difficulty_name, difficulty_modifier)
        
        # Assert
        assert "Discrétion" in result
        mock_skill_check.assert_called_once_with(
            skill_name=skill_name,
            character_json=character_json,
            difficulty_name=difficulty_name,
            difficulty_modifier=difficulty_modifier
        )

    @patch('back.services.skill_service.log_debug')
    @patch('back.services.skill_service.skill_check_with_character')
    def test_perform_skill_check_logs_debug(self, mock_skill_check, mock_log_debug):
        """
        ### test_perform_skill_check_logs_debug
        **Description:** Vérifie que les logs de debug sont correctement appelés.
        **Paramètres:** Aucun.
        **Retour:** Aucun.
        """
        # Arrange
        mock_skill_check.return_value = "Test result"
        
        skill_name = "Investigation"
        character_json = '{"competences": {"Investigation": 70}}'
        difficulty_name = "Facile"
        difficulty_modifier = -5
        
        # Act
        result = perform_skill_check_with_character(skill_name, character_json, difficulty_name, difficulty_modifier)
        
        # Assert
        mock_log_debug.assert_called_once_with(
            "Test de compétence LLM avec personnage",
            action="perform_skill_check_with_character",
            skill_name=skill_name,
            difficulty_name=difficulty_name,
            difficulty_modifier=difficulty_modifier
        )
