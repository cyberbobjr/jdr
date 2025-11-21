import random
from typing import Dict, Any
from pydantic_ai import RunContext
from back.services.game_session_service import GameSessionService
from back.services.character_service import CharacterService
from back.models.domain.character import Character
from back.utils.logger import log_debug


def skill_check_with_character(
    ctx: RunContext[GameSessionService], 
    skill_name: str, 
    difficulty_name: str = "normal", 
    difficulty_modifier: int = 0
) -> str:
    """
    Performs a skill check using the session character's data.
    
    This tool resolves skill checks by:
    1. Looking up the skill in the character's skills groups
    2. Falling back to base stats if the skill is not trained
    3. Applying difficulty modifiers
    4. Rolling 1d100 and determining success/failure with degrees
    
    Args:
        skill_name (str): Name of the skill or stat to test (e.g., "perception", "strength", "acrobatics").
        difficulty_name (str): Difficulty level ("favorable", "normal", "unfavorable"). Default: "normal".
        difficulty_modifier (int): Additional difficulty modifier (optional, default 0).
    
    Returns:
        dict: Detailed result of the test including roll, target, success status, and degree.
    """
    try:
        # Get character via CharacterService
        character_service: CharacterService = CharacterService(ctx.deps.character_id)
        character: Character = character_service.get_character()
        
        # Determine the skill value to use for the test
        skill_value: int = 0
        source_used: str = ""
        
        # Normalize skill_name to lowercase for comparison
        skill_name_lower: str = skill_name.lower().replace(" ", "_")
        
        # 1. Check if it's a direct stat (strength, constitution, agility, intelligence, wisdom, charisma)
        stat_mapping: Dict[str, str] = {
            "strength": "strength",
            "constitution": "constitution",
            "agility": "agility",
            "intelligence": "intelligence",
            "wisdom": "wisdom",
            "charisma": "charisma"
        }
        
        if skill_name_lower in stat_mapping:
            stat_key: str = stat_mapping[skill_name_lower]
            stat_value: int = getattr(character.stats, stat_key)
            # Convert stat to percentage-based value (stat * 5 for d100 system)
            skill_value = stat_value * 5
            source_used = f"Base stat {stat_key.title()}"
        
        # 2. Check if it's a trained skill in any skill group
        else:
            skill_found: bool = False
            skill_groups: Dict[str, Dict[str, int]] = character.skills.model_dump()
            
            for group_name, group_skills in skill_groups.items():
                if skill_name_lower in group_skills:
                    skill_rank: int = group_skills[skill_name_lower]
                    # Calculate skill value: base stat * 5 + skill rank * 10
                    # For simplicity, we'll use a default base stat of 10 if we can't determine it
                    base_stat_value: int = 10
                    skill_value = (base_stat_value * 5) + (skill_rank * 10)
                    source_used = f"Skill {skill_name} (rank {skill_rank}) in {group_name}"
                    skill_found = True
                    break
            
            # 3. If skill not found, use default value based on related stat
            if not skill_found:
                # Default to wisdom-based check
                default_stat_value: int = character.stats.wisdom
                skill_value = default_stat_value * 5
                source_used = f"Untrained skill (using Wisdom base: {default_stat_value})"
        
        # Difficulty modifiers
        difficulty_modifiers: Dict[str, int] = {
            "favorable": -20,
            "normal": 0,
            "unfavorable": 20
        }
        
        base_difficulty: int = difficulty_modifiers.get(difficulty_name.lower(), 0)
        total_difficulty: int = base_difficulty + difficulty_modifier
        
        # Roll 1d100
        roll: int = random.randint(1, 100)
        target: int = skill_value - total_difficulty
        success: bool = roll <= target
        
        # Calculate degrees of success/failure
        margin: int = abs(roll - target)
        if success:
            if margin >= 50:
                degree: str = "Critical Success"
            elif margin >= 30:
                degree = "Excellent Success"
            elif margin >= 10:
                degree = "Good Success"
            else:
                degree = "Simple Success"
        else:
            if margin >= 50:
                degree = "Critical Failure"
            elif margin >= 30:
                degree = "Severe Failure"
            elif margin >= 10:
                degree = "Moderate Failure"
            else:
                degree = "Simple Failure"
        
        result_message: str = (
            f"Skill check for {skill_name}: {source_used} = {skill_value}, "
            f"Roll 1d100 = {roll}, Target = {target} ({skill_value} - {total_difficulty}), "
            f"Result: **{degree}**"
        )
        
        log_debug(
            "Tool skill_check_with_character called", 
            tool="skill_check_with_character", 
            player_id=str(ctx.deps.character_id), 
            skill_name=skill_name, 
            source_used=source_used, 
            skill_value=skill_value, 
            difficulty_name=difficulty_name, 
            roll=roll, 
            target=target, 
            success=success, 
            degree=degree
        )
        
        return {
            "message": result_message,
            "skill_name": skill_name,
            "roll": roll,
            "target": target,
            "success": success,
            "degree": degree,
            "source_used": source_used
        }
        
    except Exception as e:
        error_msg: str = f"Error during skill check for {skill_name}: {str(e)}"
        log_debug(
            "Error in skill_check_with_character", 
            error=str(e), 
            player_id=str(ctx.deps.character_id), 
            skill_name=skill_name
        )
        return {"error": error_msg}


# Tool definition removed - now handled directly by PydanticAI agent
