"""
Scenario management tools for the narrative agent.
"""

from typing import Literal
from pydantic_ai import RunContext
from back.services.game_session_service import GameSessionService
from back.graph.dto.scenario import ScenarioEndPayload
from back.utils.logger import log_debug


def end_scenario_tool(
    ctx: RunContext[GameSessionService],
    outcome: Literal["success", "failure"],
    summary: str,
    xp_reward: int = 0,
    gold_reward: int = 0
) -> ScenarioEndPayload:
    """
    End the current scenario.
    
    Use this tool when the player achieves or fails the main objective of the scenario.
    The tool will signal the end of the scenario and apply any rewards.
    
    Args:
        outcome (Literal["success", "failure"]): The outcome of the scenario.
            - "success": The player achieved the main objective.
            - "failure": The player failed the main objective irreversibly.
        summary (str): A narrative summary of how the scenario concluded.
        xp_reward (int): XP to award to the character (for success). Default: 0.
        gold_reward (int): Gold to award to the character (for success). Default: 0.
    
    Returns:
        ScenarioEndPayload: Structured payload containing the scenario end information.
    
    Important:
        - Do NOT use this tool for player death - the system handles that automatically.
        - After calling this tool, provide a final narrative message to close the adventure.
    """
    log_debug(
        "Tool end_scenario_tool called",
        tool="end_scenario_tool",
        session_id=str(ctx.deps.session_id),
        outcome=outcome,
        xp_reward=xp_reward,
        gold_reward=gold_reward
    )
    
    # Apply rewards if success
    if outcome == "success" and ctx.deps.character_service:
        if xp_reward > 0:
            ctx.deps.character_service.apply_xp(xp_reward)
            log_debug(
                "XP reward applied",
                character_id=str(ctx.deps.character_id),
                xp=xp_reward
            )
        
        if gold_reward > 0:
            ctx.deps.character_service.add_gold(gold_reward)
            log_debug(
                "Gold reward applied",
                character_id=str(ctx.deps.character_id),
                gold=gold_reward
            )
    
    # Build rewards dict
    rewards = None
    if xp_reward > 0 or gold_reward > 0:
        rewards = {"xp": xp_reward, "gold": gold_reward}
    
    return ScenarioEndPayload(
        outcome=outcome,
        summary=summary,
        rewards=rewards
    )
