import random
from pydantic_ai import RunContext
from back.utils.logger import log_debug
from back.services.session_service import SessionService
from back.services.character_service import CharacterService

# Mapping des compétences vers les caractéristiques de base
SKILL_TO_CHARACTERISTIC = {
    "Perception": "Intuition",
    "Investigation": "Raisonnement", 
    "Discrétion": "Agilité",
    "Athlétisme": "Force",
    "Endurance": "Constitution",
    "Commandement": "Présence",
    "Persuasion": "Présence",
    "Intimidation": "Présence",
    "Tromperie": "Présence",
    "Empathie": "Intuition",
    "Médecine": "Raisonnement",
    "Survie": "Intuition",
    "Navigation": "Raisonnement",
    "Équitation": "Agilité",
    "Natation": "Constitution",
    "Escalade": "Force",
    "Saut": "Force",
    "Course": "Constitution",
    "Acrobatie": "Agilité",
    "Lancer": "Agilité",
    "Arts": "Présence",
    "Artisanat": "Agilité",
    "Érudition": "Raisonnement",
    "Herboristerie": "Raisonnement",
    "Soins": "Intuition",
    "Musique": "Présence",
    "Comédie": "Présence"
}

def skill_check_with_character(ctx: RunContext[SessionService], skill_name: str, difficulty_name: str = "Moyenne", difficulty_modifier: int = 0) -> str:
    """
    Effectue un test de compétence en utilisant les données du personnage de la session.

    Args:
        skill_name (str): Nom de la compétence/caractéristique testée (ex: "Perception", "Force", "Discrétion").
        difficulty_name (str): Nom de la difficulté ("Facile", "Moyenne", "Difficile", "Très Difficile").
        difficulty_modifier (int): Modificateur additionnel de difficulté (optionnel, par défaut 0).
    
    Returns:
        str: Résultat détaillé du test avec jet de dé, calculs et interprétation.
    """
    try:
        # Récupérer la fiche du personnage via CharacterService
        character_service = CharacterService(ctx.deps.character_id)
        character = character_service.get_character(ctx.deps.character_id)
        character_data = character.dict()  # Convertir en dict Python
        
        # Extraction des compétences et caractéristiques
        competences = character_data.get("competences", {})
        caracteristiques = character_data.get("caracteristiques", {})
        culture_bonuses = character_data.get("culture_bonuses", {})
        
        # Déterminer la valeur à utiliser pour le test
        skill_value = 0
        source_used = ""
        
        # 1. Vérifier d'abord si c'est une compétence directe
        if skill_name in competences:
            skill_value = competences[skill_name]
            source_used = f"Compétence {skill_name}"
        
        # 2. Vérifier les bonus culturels
        elif skill_name in culture_bonuses:
            base_char = SKILL_TO_CHARACTERISTIC.get(skill_name, "Raisonnement")
            char_value = caracteristiques.get(base_char, 50)
            culture_bonus = culture_bonuses[skill_name]
            skill_value = char_value + culture_bonus
            source_used = f"{base_char} ({char_value}) + Bonus Culturel {skill_name} ({culture_bonus})"
        
        # 3. Vérifier si c'est une caractéristique directe
        elif skill_name in caracteristiques:
            skill_value = caracteristiques[skill_name]
            source_used = f"Caractéristique {skill_name}"
        
        # 4. Mapper vers la caractéristique de base
        elif skill_name in SKILL_TO_CHARACTERISTIC:
            base_char = SKILL_TO_CHARACTERISTIC[skill_name]
            skill_value = caracteristiques.get(base_char, 50)
            source_used = f"Caractéristique de base {base_char} (pour {skill_name})"
        
        # 5. Valeur par défaut
        else:
            skill_value = 50
            source_used = f"Valeur par défaut (compétence {skill_name} non trouvée)"
        
        # Conversion des noms de difficulté en modificateurs
        difficulty_modifiers = {
            "Facile": -20,
            "Moyenne": 0, 
            "Difficile": 20,
            "Très Difficile": 40,
            "Impossible": 60
        }
        
        base_difficulty = difficulty_modifiers.get(difficulty_name, 0)
        total_difficulty = base_difficulty + difficulty_modifier
        
        roll = random.randint(1, 100)
        target = skill_value - total_difficulty
        success = roll <= target
        
        # Calcul des degrés de réussite/échec
        margin = abs(roll - target)
        if success:
            if margin >= 50:
                degree = "Réussite Critique"
            elif margin >= 30:
                degree = "Réussite Excellente"
            elif margin >= 10:
                degree = "Réussite Bonne"
            else:
                degree = "Réussite Simple"
        else:
            if margin >= 50:
                degree = "Échec Critique"
            elif margin >= 30:
                degree = "Échec Grave"
            elif margin >= 10:
                degree = "Échec Moyen"
            else:
                degree = "Échec Simple"
        result = f"Test de {skill_name}: {source_used} = {skill_value}, Jet 1d100 = {roll}, Seuil = {target} ({skill_value} - {total_difficulty}), Résultat: **{degree}**"
        
        log_debug("Tool skill_check_with_character appelé", tool="skill_check_with_character", 
                  player_id=str(ctx.deps.character_id), skill_name=skill_name, 
                  source_used=source_used, skill_value=skill_value, difficulty_name=difficulty_name, 
                  roll=roll, target=target, success=success, degree=degree)
        return result
        
    except Exception as e:
        error_msg = f"Erreur lors du test de {skill_name}: {str(e)}"
        log_debug("Erreur dans skill_check_with_character", error=str(e), 
                  player_id=str(ctx.deps.character_id), skill_name=skill_name)
        return error_msg

# Outil principal à utiliser avec les données complètes du personnage
# Tool definition removed - now handled directly by PydanticAI agent
