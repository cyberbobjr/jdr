"""
Tests pour SkillsManager
"""

from back.models.domain.skills_manager import SkillsManager

def test_skills_manager_initialization():
    """Test l'initialisation du manager des compétences."""
    manager = SkillsManager()
    assert manager is not None
    
    # Vérifier que les données sont chargées
    skill_groups = manager.get_all_skill_groups()
    assert len(skill_groups) > 0

def test_get_all_skill_groups():
    """Test la récupération de tous les groupes de compétences."""
    manager = SkillsManager()
    groups = manager.get_all_skill_groups()
    
    assert isinstance(groups, dict)
    assert len(groups) > 0
    
    # Vérifier la structure des données
    for group_name, skills in groups.items():
        assert isinstance(group_name, str)
        assert isinstance(skills, list)
        assert len(skills) > 0
        
        for skill in skills:
            assert isinstance(skill, dict)
            assert "name" in skill
            assert "description" in skill
            assert "primary_characteristic" in skill
            assert "difficulty_levels" in skill

def test_get_skills_by_group():
    """Test la récupération des compétences par groupe."""
    manager = SkillsManager()
    all_groups = manager.get_all_skill_groups()
    
    if all_groups:
        first_group = list(all_groups.keys())[0]
        skills = manager.get_skills_by_group(first_group)
        
        assert isinstance(skills, list)
        assert len(skills) > 0
        
    # Test avec un groupe inexistant
    assert manager.get_skills_by_group("GroupeInexistant") == []

def test_get_skill_by_name():
    """Test la récupération d'une compétence par nom."""
    manager = SkillsManager()
    all_groups = manager.get_all_skill_groups()
    
    # Récupérer une compétence existante
    if all_groups:
        for skills in all_groups.values():
            if skills:
                skill_name = skills[0]["name"]
                skill_data = manager.get_skill_by_name(skill_name)
                
                assert skill_data is not None
                assert skill_data["name"] == skill_name
                break
    
    # Test avec un nom inexistant
    assert manager.get_skill_by_name("CompétenceInexistante") is None

def test_get_all_skills_flat():
    """Test la récupération de toutes les compétences dans une liste plate."""
    manager = SkillsManager()
    skills = manager.get_all_skills_flat()
    
    assert isinstance(skills, list)
    assert len(skills) > 0
    
    # Vérifier que toutes les compétences ont la structure attendue
    for skill in skills:
        assert isinstance(skill, dict)
        assert "name" in skill
        assert "group" in skill
        assert "description" in skill
        assert "primary_characteristic" in skill

def test_search_skills():
    """Test la recherche de compétences."""
    manager = SkillsManager()
    all_skills = manager.get_all_skills_flat()
    
    if all_skills:
        # Test avec une recherche qui devrait donner des résultats
        first_skill_name = all_skills[0]["name"]
        search_term = first_skill_name[:3]  # Premiers caractères
        results = manager.search_skills(search_term)
        
        assert isinstance(results, list)
        # Au moins un résultat devrait être trouvé
        assert len(results) >= 1
        
        # Vérifier que le résultat contient le terme recherché
        found = any(search_term.lower() in skill["name"].lower() for skill in results)
        assert found

def test_get_skills_by_characteristic():
    """Test la récupération des compétences par caractéristique principale."""
    manager = SkillsManager()
    
    # Test avec une caractéristique courante
    skills = manager.get_skills_by_characteristic("Force")
    assert isinstance(skills, list)
    
    # Vérifier que toutes les compétences retournées ont bien cette caractéristique
    for skill in skills:
        assert skill["primary_characteristic"] == "Force"

def test_get_group_names():
    """Test la récupération des noms de groupes."""
    manager = SkillsManager()
    group_names = manager.get_group_names()
    
    assert isinstance(group_names, list)
    assert len(group_names) > 0
    
    # Vérifier que tous sont des chaînes
    for name in group_names:
        assert isinstance(name, str)
        assert len(name) > 0
