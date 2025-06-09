"""
Test de refactorisation des outils de compétences - Version simple et fonctionnelle.
"""

import pytest
import sys
from pathlib import Path

# Configuration du path pour les imports
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from back.services.session_service import SessionService
from back.tools.skill_tools import skill_check_with_character


class TestSkillRefactoringSimple:
    """Tests de validation de la refactorisation des outils de compétences."""
    
    def test_character_perform_skill_check_removed(self):
        """Vérifie que character_perform_skill_check a été supprimé."""
        with pytest.raises(ImportError):
            from back.tools.character_tools import character_perform_skill_check
    
    def test_skill_check_with_character_available(self):
        """Vérifie que skill_check_with_character est disponible."""
        assert callable(skill_check_with_character)
    
    def test_skill_check_direct(self):
        """Test direct de skill_check_with_character."""
        # Utiliser un personnage existant
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        session_id = "test_skill_refactoring_simple"
        
        # Créer la session
        session = SessionService(session_id, character_id, "Test")
        
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
        
        print("✅ Tous les tests de refactorisation sont passés !")
    
    def test_session_service_character_id(self):
        """Vérifie que SessionService définit correctement character_id."""
        character_id = "79e55c14-7dd5-4189-b209-ea88f6d067eb"
        session_id = "test_character_id"
        
        session = SessionService(session_id, character_id, "Test")
        assert session.character_id == character_id
        assert session.character_id is not None


if __name__ == "__main__":
    # Exécution directe pour tests rapides
    test = TestSkillRefactoringSimple()
    
    print("🧪 Test de refactorisation des outils de compétences")
    print("=" * 55)
    
    try:
        test.test_character_perform_skill_check_removed()
        print("✅ character_perform_skill_check supprimé")
        
        test.test_skill_check_with_character_available()
        print("✅ skill_check_with_character disponible")
        
        test.test_skill_check_direct()
        print("✅ Tests fonctionnels passés")
        
        test.test_session_service_character_id()
        print("✅ SessionService fonctionne correctement")
        
        print("\n🎉 REFACTORISATION VALIDÉE AVEC SUCCÈS !")
        
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")
        import traceback
        traceback.print_exc()
