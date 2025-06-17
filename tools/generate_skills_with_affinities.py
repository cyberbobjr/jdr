"""
Script pour injecter automatiquement la propriété 'cultures' dans chaque compétence de skills_for_llm.json
selon le mapping défini dans skills_affinities.json.

Usage :
    python generate_skills_with_affinities.py

Ce script modifie skills_for_llm.json en ajoutant ou mettant à jour la propriété 'cultures' pour chaque compétence.
"""
import json

SKILLS_FILE = "data/skills_for_llm.json"
AFFINITIES_FILE = "data/skills_affinities.json"


def inject_cultures_into_skills(skills_file: str, affinities_file: str) -> None:
    """
    Ajoute la propriété 'cultures' à chaque compétence selon le mapping d'affinités.
    Paramètres :
    - skills_file (str) : chemin du fichier JSON des compétences.
    - affinities_file (str) : chemin du fichier JSON des affinités.
    Retour : None
    """
    with open(skills_file, encoding="utf-8") as f:
        skills_data = json.load(f)
    with open(affinities_file, encoding="utf-8") as f:
        affinities = json.load(f)

    for group in skills_data["skills_for_llm"]["skill_groups"].values():
        for skill in group:
            name = skill["name"]
            skill["cultures"] = affinities.get(name, [])

    with open(skills_file, "w", encoding="utf-8") as f:
        json.dump(skills_data, f, ensure_ascii=False, indent=2)


def main():
    inject_cultures_into_skills(SKILLS_FILE, AFFINITIES_FILE)
    print("Injection des cultures terminée dans skills_for_llm.json.")

if __name__ == "__main__":
    main()
