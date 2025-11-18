# Unit business logic (SRP)

import os
from back.models.schema import ScenarioList, ScenarioStatus
from back.utils.logger import log_debug
from back.services.character_service import CharacterService
from back.config import get_data_dir


class ScenarioService:
    """
    ### list_scenarios
    **Description:** Lists available scenarios and those in progress.
    **Parameters:** None.
    **Returns:** List of `ScenarioStatus`, including name, status, and session ID (if applicable).
    """
    @staticmethod
    def list_scenarios() -> ScenarioList:
        # Define paths to scenarios and sessions directories
        scenarios_dir = os.path.join(get_data_dir(), "scenarios")
        sessions_dir = os.path.join(get_data_dir(), "sessions")

        # Available scenarios (*.md in data/scenarios)
        available = []
        if os.path.isdir(scenarios_dir):
            for fname in os.listdir(scenarios_dir):
                if fname.endswith(".md"):
                    available.append(ScenarioStatus(name=fname, status="available"))        # In-progress scenarios (UUID folders in data/sessions)
        in_progress = []
        if os.path.isdir(sessions_dir):
            for d in os.listdir(sessions_dir):
                dir_path = os.path.join(sessions_dir, d)
                if os.path.isdir(dir_path):
                    try:
                        session_id = UUID(d)

                        # Enrich with explicit names
                        scenario_name = None
                        character_name = None
                        try:
                            session_info = GameSessionService.get_session_info(str(session_id))
                            scenario_name = session_info.get("scenario_name")
                            character_id = session_info.get("character_id")

                            # Retrieve character name
                            if character_id:
                                character = CharacterService.get_character_by_id(character_id)
                                character_name = character.get("name", "Unknown") if character else "Unknown"

                        except Exception as e:
                            log_debug("Unable to retrieve enriched info for session",
                                     action="list_scenarios", session_id=str(session_id), error=str(e))

                        # Create a more explicit display name
                        display_name = str(session_id)
                        if scenario_name and character_name:
                            display_name = f"{scenario_name} - {character_name}"
                        elif scenario_name:
                            display_name = f"{scenario_name} - Session {str(session_id)[:8]}"

                        in_progress.append(ScenarioStatus(
                            name=display_name,
                            status="in_progress",
                            session_id=session_id,
                            scenario_name=scenario_name,
                            character_name=character_name
                        ))
                    except Exception:
                        continue

        log_debug("Scenario list requested", action="list_scenarios", available=len(available), in_progress=len(in_progress))
        return ScenarioList(scenarios=available + in_progress)

    @staticmethod
    def get_scenario_details(scenario_file: str) -> str:
        """
        Retrieves the content of a scenario (Markdown file) from its filename.

        Parameters:
        - scenario_file (str): The scenario file name (e.g., Les_Pierres_du_Passe.md).

        Returns:
        - str: The Markdown file content of the scenario.

        Raises:
        - FileNotFoundError: If the file does not exist.
        """
        scenario_path = os.path.join(get_data_dir(), "scenarios", scenario_file)
        if not os.path.isfile(scenario_path):
            raise FileNotFoundError(f"The scenario '{scenario_file}' does not exist.")
        with open(scenario_path, "r", encoding="utf-8") as f:
            return f.read()

