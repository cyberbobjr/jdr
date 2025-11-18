"""
Scenario router using PydanticAI GM agent.
Final version after complete migration from Haystack to PydanticAI.
"""

from fastapi import APIRouter, HTTPException

from back.services.scenario_service import ScenarioService
from back.models.schema import (
    ScenarioList,
)
from back.utils.logger import log_debug

router = APIRouter(tags=["scenario"])

@router.get("/", response_model=ScenarioList)
async def list_scenarios() -> ScenarioList:
    """
    List available scenarios and in-progress ones.

    **Response:**
    ```json
    {
        "scenarios": [
            {
                "name": "Les_Pierres_du_Passe.md",
                "status": "available",
                "session_id": null,
                "scenario_name": null,
                "character_name": null
            },
            {
                "name": "Les_Pierres_du_Passe.md - Galadhwen",
                "status": "in_progress",
                "session_id": "12345678-1234-5678-9012-123456789abc",
                "scenario_name": "Les_Pierres_du_Passe.md",
                "character_name": "Galadhwen"
            }
        ]
    }
    ```
    """
    log_debug("Endpoint call: scenarios/list_scenarios")
    scenarios: ScenarioList = ScenarioService.list_scenarios()
    return scenarios

@router.get("/{scenario_file}", response_model=str)
async def get_scenario_details(scenario_file: str) -> str:
    """
    Retrieve the content of a scenario (Markdown file) by its filename.

    **Parameters:**
    - `scenario_file` (str): The filename of the scenario (e.g., Les_Pierres_du_Passe.md).

    **Returns:**
    The Markdown content of the scenario file as a string.

    **Raises:**
    - HTTPException 404: If the scenario file does not exist.

    **Response:**
    ```
    # Scenario: The Stones of the Past

    ## Context
    The story takes place in the year 2955 of the Third Age...

    ## 1. Locations
    ### Esgalbar Village
    - **Description**: Small wooden houses village...
    ```
    """
    log_debug("Endpoint call: scenarios/get_scenario_details", scenario_file=scenario_file)
    try:
        content: str = ScenarioService.get_scenario_details(scenario_file)
        return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_file}' not found.")



