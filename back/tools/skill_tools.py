import random
from pydantic_ai import RunContext
from back.utils.logger import log_debug
from back.services.session_service import SessionService
from back.services.character_service import CharacterService

import random
from pydantic_ai import RunContext
from back.utils.logger import log_debug
from back.services.session_service import SessionService
from back.services.character_service import CharacterService
from back.models.domain.skills_manager import SkillsManager
from back.models.domain.stats_manager import StatsManager

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
    try:        # Récupérer la fiche du personnage via CharacterService
        character_service = CharacterService(ctx.deps.character_id)
        character = character_service.get_character()
        # Gérer le cas où character est un dict ou un objet Character
        if hasattr(character, 'model_dump'):
            character_data = character.model_dump()  # Objet Character
        else:
            character_data = character  # Déjà un dict        # Extraction des compétences et caractéristiques
        competences = character_data.get("competences", {})
        caracteristiques = character_data.get("caracteristiques", {})
        # Récupérer les bonus culturels depuis culture.skill_bonuses
        culture = character_data.get("culture", {})
        culture_bonuses = culture.get("skill_bonuses", {}) if culture else {}
        
        # Déterminer la valeur à utiliser pour le test
        skill_value = 0        # Récupération des managers pour les nouvelles données
        skills_manager = SkillsManager()
        characteristics_manager = StatsManager()
        
        source_used = ""
        
        # 1. Vérifier d'abord si c'est une compétence directe
        if skill_name in competences:
            skill_value = competences[skill_name]
            source_used = f"Compétence {skill_name}"
        
        # 2. Vérifier les bonus culturels
        elif skill_name in culture_bonuses:
            # Utiliser le skills_manager pour trouver la caractéristique de base
            skill_data = skills_manager.get_skill_by_name(skill_name)
            if skill_data:
                base_char = skill_data.get("primary_characteristic", "Raisonnement")
            else:
                base_char = "Raisonnement"
            
            char_value = caracteristiques.get(base_char, 50)
            culture_bonus = culture_bonuses[skill_name]
            skill_value = char_value + culture_bonus
            source_used = f"{base_char} ({char_value}) + Bonus Culturel {skill_name} ({culture_bonus})"
        
        # 3. Vérifier si c'est une caractéristique directe
        elif skill_name in caracteristiques:
            skill_value = caracteristiques[skill_name]
            source_used = f"Caractéristique {skill_name}"
        
        # 4. Mapper vers la caractéristique de base via le skills_manager
        else:
            skill_data = skills_manager.get_skill_by_name(skill_name)
            if skill_data:
                base_char = skill_data.get("primary_characteristic", "Raisonnement")
                skill_value = caracteristiques.get(base_char, 50)
                source_used = f"Caractéristique de base {base_char} (pour {skill_name})"
            else:
                # Valeur par défaut
                skill_value = 50
                source_used = f"Valeur par défaut (compétence {skill_name} non trouvée)"
        
        # Simplified difficulty modifiers for modern gameplay
        difficulty_modifiers = {
            "favorable": -20,
            "normal": 0,
            "unfavorable": 20
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
