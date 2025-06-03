from back.tools.skill_tools import skill_check_with_character
from back.utils.logger import log_debug

# Logique métier unitaire (SRP)

def perform_skill_check_with_character(skill_name: str, character_json: str, difficulty_name: str = "Moyenne", difficulty_modifier: int = 0) -> str:
    """
    ### perform_skill_check_with_character
    **Description :** Effectue un test de compétence en utilisant l'outil Haystack skill_check_with_character.
    **Paramètres :**
    - `skill_name` (str) : Nom de la compétence/caractéristique testée.
    - `character_json` (str) : Données complètes du personnage au format JSON.
    - `difficulty_name` (str) : Nom de la difficulté ("Facile", "Moyenne", "Difficile", "Très Difficile").
    - `difficulty_modifier` (int) : Modificateur additionnel de difficulté.
    **Retour :**
    - (str) : Résultat détaillé du test avec jet de dé, calculs et interprétation.
    """
    log_debug("Test de compétence LLM avec personnage", action="perform_skill_check_with_character", 
              skill_name=skill_name, difficulty_name=difficulty_name, difficulty_modifier=difficulty_modifier)
    return skill_check_with_character(skill_name=skill_name, character_json=character_json, 
                                     difficulty_name=difficulty_name, difficulty_modifier=difficulty_modifier)
