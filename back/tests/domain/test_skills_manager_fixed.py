"""
Tests unitaires pour SkillsManager (version corrigée).
"""
from back.models.domain.skills_manager import SkillsManager

class TestSkillsManagerFixed:
    def test_skills_manager_initialization(self):
        """Test l'initialisation du manager des compétences."""
        manager = SkillsManager()
        assert manager is not None
        assert hasattr(manager, 'skills_data')

    def test_get_all_skills(self):
        """Test la récupération de toutes les compétences."""
        manager = SkillsManager()
        skills = manager.get_all_skills()
        
        assert isinstance(skills, list)
        assert len(skills) > 0
        
        # Vérifier la structure des compétences
        for skill in skills:
            assert isinstance(skill, dict)
            assert "name" in skill
            assert "group" in skill

    def test_get_skill_by_name(self):
        """Test la récupération d'une compétence par nom."""
        manager = SkillsManager()
        all_skills = manager.get_all_skills()
        
        if all_skills:
            first_skill = all_skills[0]
            skill_name = first_skill["name"]
            skill_data = manager.get_skill_by_name(skill_name)
            
            assert skill_data is not None
            assert isinstance(skill_data, dict)
            assert skill_data["name"] == skill_name

    def test_get_skills_by_group(self):
        """Test la récupération des compétences par groupe."""
        manager = SkillsManager()
        all_skills = manager.get_all_skills()
        
        if all_skills:
            # Prendre le groupe de la première compétence
            first_skill = all_skills[0]
            group_name = first_skill["group"]
            
            skills_in_group = manager.get_skills_by_group(group_name)
            
            assert isinstance(skills_in_group, list)
            assert len(skills_in_group) > 0
            
            # Vérifier que toutes les compétences appartiennent au bon groupe
            for skill in skills_in_group:
                assert skill["group"] == group_name

    def test_get_difficulty_modifier(self):
        """Test la récupération du modificateur de difficulté."""
        manager = SkillsManager()
        
        # Test avec des difficultés standard
        difficulties = ["Facile", "Moyenne", "Difficile", "Très Difficile"]
        for difficulty in difficulties:
            modifier = manager.get_difficulty_modifier(difficulty)
            assert isinstance(modifier, int)

    def test_get_all_difficulty_levels(self):
        """Test la récupération de tous les niveaux de difficulté."""
        manager = SkillsManager()
        difficulties = manager.get_all_difficulty_levels()
        
        assert isinstance(difficulties, dict)
        assert len(difficulties) > 0
        
        # Vérifier la structure
        for diff_name, diff_data in difficulties.items():
            assert isinstance(diff_name, str)
            assert isinstance(diff_data, dict)

    def test_search_skills_by_keyword(self):
        """Test la recherche de compétences par mot-clé."""
        manager = SkillsManager()
        all_skills = manager.get_all_skills()
        
        if all_skills:
            # Utiliser le nom de la première compétence comme mot-clé
            first_skill = all_skills[0]
            keyword = first_skill["name"][:3]  # Prendre les 3 premiers caractères
            
            results = manager.search_skills_by_keyword(keyword)
            assert isinstance(results, list)

    def test_get_skills_by_characteristic(self):
        """Test la récupération des compétences par caractéristique."""
        manager = SkillsManager()
        
        # Test avec une caractéristique courante
        skills = manager.get_skills_by_characteristic("Force")
        assert isinstance(skills, list)
        
        # Vérifier que toutes les compétences retournées ont bien cette caractéristique
        for skill in skills:
            assert "characteristic" in skill or "primary_characteristic" in skill

    def test_suggest_skill_for_action(self):
        """Test la suggestion de compétences pour une action."""
        manager = SkillsManager()
        
        # Test avec une description d'action
        suggestions = manager.suggest_skill_for_action("escalader un mur")
        assert isinstance(suggestions, list)
