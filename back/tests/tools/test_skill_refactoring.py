"""
### test_skill_refactoring
**Description :** Tests de validation de la refactorisation des outils de compétences.
Vérifie que skill_check_with_character fonctionne correctement après suppression de character_perform_skill_check.
"""

import pytest
import sys
from pathlib import Path

# Ajouter le répertoire back au PYTHONPATH pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from back.services.session_service import SessionService
from back.tools.skill_tools import skill_check_with_character


class TestSkillRefactoring:
    """
    ### TestSkillRefactoring
    **Description :** Suite de tests pour valider la refactorisation des outils de compétences.
    """
    
    @pytest.fixture
    def character_id(self):
        """
        ### character_id
        **Description :** Fixture qui retourne l'ID d'un personnage existant pour les tests.
        **Returns :** ID du personnage de test.
        """
        return "79e55c14-7dd5-4189-b209-ea88f6d067eb"
    
    @pytest.fixture
    def session_service(self, character_id):
        """
        ### session_service
        **Description :** Fixture qui crée un service de session pour les tests.
        **Parameters :**
        - `character_id` (str): ID du personnage à associer à la session.
        **Returns :** Instance de SessionService configurée pour les tests.
        """
        session_id = "test_skill_refactoring"
        return SessionService(session_id, character_id, "Test Scenario")
    
    @pytest.fixture
    def mock_context(self, session_service):
        """
        ### mock_context
        **Description :** Fixture qui crée un contexte d'exécution simulé pour les tests d'outils.
        **Parameters :**
        - `session_service` (SessionService): Service de session à utiliser.
        **Returns :** Contexte simulé avec deps.
        """
        class MockRunContext:
            def __init__(self, session):
                self.deps = session
        
        return MockRunContext(session_service)
    
    def test_character_perform_skill_check_removed(self):
        """
        ### test_character_perform_skill_check_removed
        **Description :** Vérifie que character_perform_skill_check a été supprimé des imports.
        """
        # Tenter d'importer character_perform_skill_check devrait échouer
        with pytest.raises(ImportError):
            from tools.character_tools import character_perform_skill_check
    
    def test_skill_check_with_character_available(self):
        """
        ### test_skill_check_with_character_available
        **Description :** Vérifie que skill_check_with_character est disponible et importable.
        """
        # L'import devrait réussir
        from tools.skill_tools import skill_check_with_character
        assert callable(skill_check_with_character)
    
    def test_skill_check_characteristic(self, mock_context):
        """
        ### test_skill_check_characteristic
        **Description :** Teste un jet de caractéristique directe.
        **Parameters :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        result = skill_check_with_character(mock_context, "Force", "Moyenne")
        
        assert isinstance(result, str)
        assert "Force" in result
        assert "Jet 1d100" in result
        assert "Résultat:" in result
    
    def test_skill_check_competence(self, mock_context):
        """
        ### test_skill_check_competence
        **Description :** Teste un jet de compétence spécialisée.
        **Parameters :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        result = skill_check_with_character(mock_context, "Perception", "Facile")
        
        assert isinstance(result, str)
        assert "Perception" in result
        assert "Jet 1d100" in result
        assert "Résultat:" in result
    
    def test_skill_check_mapped_skill(self, mock_context):
        """
        ### test_skill_check_mapped_skill
        **Description :** Teste un jet de compétence mappée vers une caractéristique.
        **Parameters :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        result = skill_check_with_character(mock_context, "Survie", "Difficile")
        
        assert isinstance(result, str)
        assert "Survie" in result
        assert "Jet 1d100" in result
        assert "Résultat:" in result
    
    def test_skill_check_unknown_skill(self, mock_context):
        """
        ### test_skill_check_unknown_skill
        **Description :** Teste un jet de compétence inexistante (valeur par défaut).
        **Parameters :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        result = skill_check_with_character(mock_context, "Magie Ancienne", "Très Difficile")
        
        assert isinstance(result, str)
        assert "Magie Ancienne" in result
        assert "Jet 1d100" in result
        assert "Résultat:" in result
        assert "Valeur par défaut" in result
    
    def test_skill_check_various_difficulties(self, mock_context):
        """
        ### test_skill_check_various_difficulties
        **Description :** Teste différents niveaux de difficulté.
        **Parameters :**
        - `mock_context` : Contexte d'exécution simulé.
        """
        difficulties = ["Facile", "Moyenne", "Difficile", "Très Difficile", "Impossible"]
        
        for difficulty in difficulties:
            result = skill_check_with_character(mock_context, "Force", difficulty)
            
            assert isinstance(result, str)
            assert "Force" in result
            assert "Jet 1d100" in result
            assert "Résultat:" in result
    
    def test_character_service_integration(self, mock_context, character_id):
        """
        ### test_character_service_integration
        **Description :** Vérifie que l'outil récupère correctement les données via CharacterService.
        **Parameters :**
        - `mock_context` : Contexte d'exécution simulé.
        - `character_id` (str): ID du personnage à tester.
        """
        # Vérifier que le character_id est bien défini dans le contexte
        assert mock_context.deps.character_id == character_id
        
        # L'outil devrait pouvoir récupérer les données du personnage
        result = skill_check_with_character(mock_context, "Force", "Moyenne")
        
        # Le résultat ne devrait pas contenir d'erreur de récupération de personnage
        assert "Erreur lors du test" not in result
        assert isinstance(result, str)
        assert len(result) > 0
