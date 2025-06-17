import json

SKILLS_FILE = "data/skills_for_llm.json"
AFFINITIES_FILE = "data/skills_affinities.json"

def test_cultures_injection():
    """
    Vérifie que chaque compétence possède bien la propriété 'cultures' et qu'elle correspond au mapping d'affinités.
    """
    with open(SKILLS_FILE, encoding="utf-8") as f:
        skills_data = json.load(f)
    with open(AFFINITIES_FILE, encoding="utf-8") as f:
        affinities = json.load(f)
    for group in skills_data["skills_for_llm"]["skill_groups"].values():
        for skill in group:
            name = skill["name"]
            assert "cultures" in skill, f"La compétence '{name}' n'a pas de champ 'cultures'"
            assert skill["cultures"] == affinities.get(name, []), f"Mismatch cultures pour {name}"

def test_affinities_mapping_completeness():
    """
    Vérifie que toutes les compétences du mapping existent dans le fichier des compétences.
    """
    with open(SKILLS_FILE, encoding="utf-8") as f:
        skills_data = json.load(f)
    all_skill_names = set()
    for group in skills_data["skills_for_llm"]["skill_groups"].values():
        for skill in group:
            all_skill_names.add(skill["name"])
    with open(AFFINITIES_FILE, encoding="utf-8") as f:
        affinities = json.load(f)
    for skill_name in affinities:
        assert skill_name in all_skill_names, f"Le mapping d'affinité fait référence à une compétence inconnue : {skill_name}"
