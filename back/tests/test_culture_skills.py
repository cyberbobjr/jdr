
# Tests unitaires pour les skills de culture

def test_culture_skills_structure():
    """
    Vérifie que chaque skill de culture possède les champs requis et la propriété 'culture'.
    """
    import json
    with open('data/skills_for_llm.json', encoding='utf-8') as f:
        data = json.load(f)
    culture_skills = data['skills_for_llm']['skill_groups']['Culture']
    for skill in culture_skills:
        assert 'name' in skill
        assert 'description' in skill
        assert 'characteristics' in skill
        assert 'examples' in skill
        assert 'culture' in skill
        assert isinstance(skill['culture'], list)
        assert len(skill['culture']) > 0

def test_culture_skills_uniqueness():
    """
    Vérifie qu'aucun skill de culture n'est dupliqué par nom et culture.
    """
    import json
    with open('data/skills_for_llm.json', encoding='utf-8') as f:
        data = json.load(f)
    culture_skills = data['skills_for_llm']['skill_groups']['Culture']
    seen = set()
    for skill in culture_skills:
        key = (skill['name'], tuple(skill['culture']))
        assert key not in seen, f"Doublon trouvé pour {key}"
        seen.add(key)
