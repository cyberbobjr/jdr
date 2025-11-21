"""
Scenario-related DTOs for graph state management.
"""

from pydantic import BaseModel
from typing import Literal


class ScenarioEndPayload(BaseModel):
    """
    ### ScenarioEndPayload
    **Description:** Payload returned when a scenario ends.
    This is used to signal the end of a scenario and transition the game state.
    
    **Attributes:**
    - `outcome` (Literal["success", "failure", "death"]): Type of ending.
    - `summary` (str): Narrative summary of how the scenario ended.
    - `rewards` (dict[str, int] | None): Optional rewards (xp, gold) for success.
    """
    outcome: Literal["success", "failure", "death"]
    summary: str
    rewards: dict[str, int] | None = None
