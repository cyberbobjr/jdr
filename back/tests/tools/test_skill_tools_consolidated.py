"""
Consolidated tests for skill-related tools.
Combines tests from:
- test_skill_refactoring.py
- test_skill_refactoring_final.py
- test_skill_tools.py
"""

import pytest
import sys
from pathlib import Path

# Configuration du path pour les imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from back.services.session_service import SessionService
from back.tools.skill_tools import skill_check_with_character


class TestSkillToolsConsolidated:
    """Test suite for all skill-related tools"""
    
    @pytest.fixture
    def character_id(self, character_79e55c14):
        """Fixture qui retourne l'ID d'un personnage existant pour les tests."""
        return "79e55c14-7dd5-4189-b209-ea88f6d067eb"
    
    @pytest.fixture
    def session_service(self, character_id):
        """Fixture qui crée un service de session pour les tests."""
        session_id = "test_skill_consolidated"
        return SessionService(session_id, character_id, "Test Scenario")
    
    @pytest.fixture
    def mock_context(self, session_service):
        """Fixture qui crée un contexte d'exécution simulé pour les tests d'outils."""
        class MockRunContext:
            def __init__(self, session):
                self.deps = session
        
        return MockRunContext(session_service)

    def test_character_perform_skill_check_removed(self):
        """Vérifie que character_perform_skill_check a été supprimé des imports."""
        with pytest.raises(ImportError):
            from back.tools.character_tools import character_perform_skill_check

    def test_skill_check_with_character_available(self):
        """Vérifie que skill_check_with_character est disponible et importable."""
        assert callable(skill_check_with_character)

    def test_skill_check_characteristic(self, mock_context):
        """Teste un jet de caractéristique directe."""
        result = skill_check_with_character(mock_context, "Force", "Moyenne")
        
        assert isinstance(result, str)
        assert "Force" in result
        assert "Jet 1d100" in result
        assert "Résultat:" in result

    def test_skill_check_competence(self, mock_context):
        """Teste un jet de compétence spécialisée."""
        result = skill_check_with_character(mock_context, "Perception", "Facile")
        
        assert isinstance(result, str)
        assert "Perception" in result
        assert "Jet 1d100" in result
        assert "Résultat:" in result

    def test_skill_check_mapped_skill(self, mock_context):
        """Teste un jet de compétence mappée vers une caractéristique."""
        result = skill_check_with_character(mock_context, "Survie", "Difficile")
        
        assert isinstance(result, str)
        assert "Survie" in result
        assert "Jet 1d100" in result
        assert "Résultat:" in result

    def test_skill_check_unknown_skill(self, mock_context):
        """Teste un jet de compétence inexistante (valeur par défaut)."""
        result = skill_check_with_character(mock_context, "Magie Ancienne", "Très Difficile")
        
        assert isinstance(result, str)
        assert "Magie Ancienne" in result
        assert "Jet 1d100" in result
        assert "Résultat:" in result
        assert "Valeur par défaut" in result

    def test_skill_check_various_difficulties(self, mock_context):
        """Teste différents niveaux de difficulté."""
        difficulties = ["Facile", "Moyenne", "Difficile", "Très Difficile", "Impossible"]
        
        for difficulty in difficulties:
            result = skill_check_with_character(mock_context, "Force", difficulty)
            
            assert isinstance(result, str)
            assert "Force" in result
            assert "Jet 1d100" in result
            assert "Résultat:" in result

    def test_character_service_integration(self, mock_context, character_id):
        """Vérifie que l'outil récupère correctement les données via CharacterService."""
        # Vérifier que le character_id est bien défini dans le contexte
        assert mock_context.deps.character_id == character_id
        
        # L'outil devrait pouvoir récupérer les données du personnage
        result = skill_check_with_character(mock_context, "Force", "Moyenne")
        
        # Le résultat ne devrait pas contenir d'erreur de récupération de personnage
        assert "Erreur lors du test" not in result
        assert isinstance(result, str)
        assert len(result) > 0

    def test_session_service_character_id(self, character_id):
        """Vérifie que SessionService définit correctement character_id."""
        session_id = "test_character_id"
        session = SessionService(session_id, character_id, "Test")
        
        assert session.character_id == character_id
        assert session.character_id is not None   
        def test_skill_direct_execution(self, character_id):
            """Test direct de skill_check_with_character avec session réelle."""
        # Créer la session
        session = SessionService("test_direct", character_id, "Test")
        
        # Créer un contexte simulé
        class MockContext:
            def __init__(self, session):
                self.deps = session
        
        context = MockContext(session)
        
        # Tester différentes compétences
        result = skill_check_with_character(context, "Force", "Moyenne")
        assert isinstance(result, str)
        assert "Force" in result
        assert "Jet 1d100" in result
        assert "Résultat:" in result
        
        # Test avec compétence mappée
        result = skill_check_with_character(context, "Perception", "Facile")
        assert isinstance(result, str)
        assert "Perception" in result
        
        # Test avec compétence inexistante
        result = skill_check_with_character(context, "Magie Ancienne", "Difficile")
        assert isinstance(result, str)
        assert "Valeur par défaut" in result


if __name__ == "__main__":
    # Exécution directe pour tests rapides
    import traceback
    
    print("🧪 Tests consolidés des outils de compétences")
    print("=" * 50)
    
    try:
        test = TestSkillToolsConsolidated()
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        
        test.test_character_perform_skill_check_removed()
        print("✅ character_perform_skill_check supprimé")
        
        test.test_skill_check_with_character_available()
        print("✅ skill_check_with_character disponible")
        
        test.test_skill_direct_execution(character_id)
        print("✅ Tests fonctionnels passés")
        
        test.test_session_service_character_id(character_id)
        print("✅ SessionService fonctionne correctement")
        
        print("\n🎉 TOUS LES TESTS CONSOLIDÉS PASSÉS !")
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        traceback.print_exc()
