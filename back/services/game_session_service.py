"""
Service for managing role-playing game sessions.
Handles loading and saving of history, as well as character and scenario data.
Refactored to use specialized services (Phase 3).
"""

import os
import pathlib
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4

from pydantic_ai import ModelMessage

from back.models.domain.character import Character
from back.services.character_data_service import CharacterDataService
from back.services.character_service import CharacterService
from back.services.equipment_service import EquipmentService
from back.storage.pydantic_jsonl_store import PydanticJsonlStore
from back.config import get_data_dir
from back.utils.logger import log_debug
from back.agents.PROMPT import build_system_prompt
from back.utils.exceptions import (
    ServiceNotInitializedError,
    SessionNotFoundError,
    CharacterNotFoundError
)


# History types constants
HISTORY_NARRATIVE = "narrative"
HISTORY_COMBAT = "combat"


class GameSessionService:
    """
    ### GameSessionService
    **Description:** Service responsible for managing game sessions.
    It handles the lifecycle of a session, including:
    - Loading and saving session metadata (character ID, scenario ID).
    - Managing message history for narrative and combat modes.
    - Initializing and providing access to specialized services (`CharacterService`, `EquipmentService`).
    - Building system prompts for agents.

    **Attributes:**
    - `session_id` (str): Unique identifier for the session.
    - `character_id` (Optional[str]): ID of the character associated with the session.
    - `scenario_id` (str): ID of the scenario associated with the session.
    - `data_service` (Optional[CharacterDataService]): Service for character data persistence.
    - `character_service` (Optional[CharacterService]): Service for character business logic.
    - `equipment_service` (Optional[EquipmentService]): Service for equipment management.
    """

    def __init__(self, session_id: str, character_id: Optional[str] = None, scenario_id: Optional[str] = None) -> None:
        """
        ### __init__
        **Description:** Initializes the session service with a session identifier.
        If the session exists, it loads the data. If not, and creation parameters are provided, it creates a new session.

        **Parameters:**
        - `session_id` (str): Unique session identifier.
        - `character_id` (Optional[str]): Character ID (required for creating a new session).
        - `scenario_id` (Optional[str]): Scenario ID (required for creating a new session).
        
        **Returns:** None.

        **Raises:**
        - `SessionNotFoundError`: If the session does not exist and creation parameters are missing.
        """
        self.session_id = session_id
        self.character_id = character_id
        self.scenario_id: str = ""

        # Specialized services
        self.data_service: Optional[CharacterDataService] = None
        self.character_service: Optional[CharacterService] = None
        self.equipment_service: Optional[EquipmentService] = None
        self._combat_system_prompt: Optional[str] = None

        # Store is created on demand in save_history/load_history methods

        # Load session data or create a new session
        if not self._load_session_data():
            # If session doesn't exist and parameters are provided, create a new session
            if character_id and scenario_id:
                self._create_session(character_id, scenario_id)
            else:
                raise SessionNotFoundError(f"Session {session_id} does not exist and creation parameters are not provided")

    @property
    def character_data(self) -> Optional[Character]:
        """
        ### character_data
        **Description:** Returns the character data from the `CharacterService`.
        Delegates access to the specialized service to avoid state duplication.

        **Returns:**
        - `Optional[Character]`: The character object if loaded, None otherwise.
        """
        if self.character_service:
            return self.character_service.character_data
        return None

    def _load_session_data(self) -> bool:
        """
        ### _load_session_data
        **Description:** Loads session metadata (character and scenario IDs) from the file system.
        Initializes specialized services if the session exists.

        **Returns:** 
        - `bool`: True if the session exists and was loaded, False otherwise.

        **Raises:**
        - `CharacterNotFoundError`: If the referenced character file does not exist.
        - `ValueError`: If the scenario file is missing.
        - `ServiceNotInitializedError`: If services fail to initialize.
        """
        session_dir = pathlib.Path(get_data_dir()) / "sessions" / self.session_id
        if session_dir.exists() and session_dir.is_dir():
            # Load character ID
            character_file = session_dir / "character.txt"
            if character_file.exists():
                character_id = character_file.read_text(encoding='utf-8').strip()

                self.character_id = character_id  # Important: set the character_id attribute

                # Initialize specialized services for this character
                try:
                    self._initialize_services(character_id)
                except FileNotFoundError:
                    raise CharacterNotFoundError(f"Character {character_id} not found")

            # Load scenario ID
            scenario_file = session_dir / "scenario.txt"
            if scenario_file.exists():
                self.scenario_id = scenario_file.read_text(encoding='utf-8').strip()
            else:
                raise ValueError(f"Missing scenario.txt file for session '{self.session_id}'.")

            return True

        return False

    def _create_session(self, character_id: str, scenario_id: str) -> None:
        """
        ### _create_session
        **Description:** Creates a new session directory and saves initial metadata.
        Initializes specialized services for the new session.

        **Parameters:**
        - `character_id` (str): ID of the character for this session.
        - `scenario_id` (str): ID of the scenario for this session.
        
        **Returns:** None.

        **Raises:**
        - `CharacterNotFoundError`: If the character does not exist.
        - `ServiceNotInitializedError`: If services fail to initialize.
        """
        session_dir = pathlib.Path(get_data_dir()) / "sessions" / self.session_id

        # Create session directory
        session_dir.mkdir(parents=True, exist_ok=True)

        # Save character ID
        character_file = session_dir / "character.txt"
        character_file.write_text(character_id, encoding='utf-8')

        # Save scenario ID
        scenario_file = session_dir / "scenario.txt"
        scenario_file.write_text(scenario_id, encoding='utf-8')

        # Set character_id attribute
        self.character_id = character_id

        # Initialize specialized services for this character
        try:
            self._initialize_services(character_id)
        except FileNotFoundError:
            raise CharacterNotFoundError(f"Character {character_id} not found")

        self.scenario_id = scenario_id

    def _initialize_services(self, character_id: str) -> None:
        """
        ### _initialize_services
        **Description:** Initializes specialized services (`CharacterDataService`, `CharacterService`, `EquipmentService`) for the given character.

        **Parameters:**
        - `character_id` (str): ID of the character.
        
        **Returns:** None.
        """
        # Data service
        self.data_service = CharacterDataService()

        # Character service
        self.character_service = CharacterService(character_id)

        # Equipment service (depends on data service)
        self.equipment_service = EquipmentService(self.data_service)

    @staticmethod
    def list_all_sessions() -> List[Dict[str, Any]]:
        """
        ### list_all_sessions
        **Description:** Retrieves a list of all available game sessions with their metadata.

        **Returns:** 
        - `List[Dict[str, Any]]`: A list of dictionaries containing `session_id`, `character_id`, and `scenario_id` for each session.
        """
        sessions_dir = pathlib.Path(get_data_dir()) / "sessions"
        
        all_sessions = []

        if sessions_dir.exists() and sessions_dir.is_dir():
            for session_path in sessions_dir.iterdir():
                if session_path.is_dir():
                    # Load character ID
                    character_file = session_path / "character.txt"
                    if character_file.exists():
                        character_id = character_file.read_text(encoding='utf-8').strip()
                    else:
                        character_id = "Unknown"

                    # Load scenario ID
                    scenario_file = session_path / "scenario.txt"
                    if scenario_file.exists():
                        scenario_id = scenario_file.read_text(encoding='utf-8').strip()
                    else:
                        scenario_id = "Unknown"

                    all_sessions.append({
                        "session_id": session_path.name,
                        "character_id": character_id,
                        "scenario_id": scenario_id
                    })

        return all_sessions

    @staticmethod
    def start_scenario(scenario_name: str, character_id: UUID) -> Dict[str, Any]:
        """
        ### start_scenario
        **Description:** Starts a new scenario with a specific character by creating a unique session.

        **Parameters:**
        - `scenario_name` (str): The name of the scenario to start.
        - `character_id` (UUID): The unique identifier of the character.

        **Returns:**
        - `Dict[str, Any]`: A dictionary containing `session_id`, `scenario_name`, `character_id`, and a confirmation message.

        **Raises:**
        - `ValueError`: If a session already exists for this scenario and character.
        - `FileNotFoundError`: If the scenario definition does not exist.
        """
        # Check if a session already exists with the same scenario and character
        if GameSessionService.check_existing_session(scenario_name, str(character_id)):
            raise ValueError(f"A session already exists for scenario '{scenario_name}' with character {character_id}.")

        scenarios_dir = pathlib.Path(get_data_dir()) / "scenarios"
        sessions_dir = pathlib.Path(get_data_dir()) / "sessions"

        # Check if the scenario exists
        scenario_path = scenarios_dir / scenario_name
        if not scenario_path.exists():
            raise FileNotFoundError(f"The scenario '{scenario_name}' does not exist.")

        # Create a session for the scenario
        session_id = str(uuid4())
        session_dir = sessions_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        # Associate the character with the session
        character_file = session_dir / "character.txt"
        character_file.write_text(str(character_id), encoding='utf-8')

        # Store the scenario name in the session
        scenario_file = session_dir / "scenario.txt"
        scenario_file.write_text(scenario_name, encoding='utf-8')

        log_debug("Scenario started", action="start_scenario", session_id=session_id, character_id=str(character_id), scenario_name=scenario_name)
        return {
            "session_id": session_id,
            "scenario_name": scenario_name,
            "character_id": str(character_id),
            "message": f"Scenario '{scenario_name}' successfully started for character {character_id}."
        }

    @staticmethod
    def get_session_info(session_id: str) -> Dict[str, str]:
        """
        ### get_session_info
        **Description:** Retrieves metadata (character ID and scenario name) for a given session ID.

        **Parameters:**
        - `session_id` (str): The unique session identifier.

        **Returns:**
        - `Dict[str, str]`: A dictionary containing `character_id` and `scenario_name`.

        **Raises:**
        - `SessionNotFoundError`: If the session directory does not exist.
        - `FileNotFoundError`: If metadata files are missing within the session directory.
        """
        session_dir = pathlib.Path(get_data_dir()) / "sessions" / session_id

        if not session_dir.exists() or not session_dir.is_dir():
            raise SessionNotFoundError(f"The session '{session_id}' does not exist.")

        # Retrieve the character ID
        character_file = session_dir / "character.txt"
        if not character_file.exists():
            raise FileNotFoundError(f"Missing character.txt file for session '{session_id}'.")

        character_id = character_file.read_text(encoding='utf-8').strip()

        # Retrieve the scenario name
        scenario_file = session_dir / "scenario.txt"
        if not scenario_file.exists():
            raise FileNotFoundError(f"Missing scenario.txt file for session '{session_id}'.")

        scenario_name = scenario_file.read_text(encoding='utf-8').strip()

        log_debug("Session information retrieved", action="get_session_info", session_id=session_id, character_id=character_id, scenario_name=scenario_name)
        return {
            "character_id": character_id,
            "scenario_name": scenario_name
        }

    @staticmethod
    def check_existing_session(scenario_name: str, character_id: str) -> bool:
        """
        ### check_existing_session
        **Description:** Checks if a session already exists for a specific combination of scenario and character.

        **Parameters:**
        - `scenario_name` (str): The name of the scenario.
        - `character_id` (str): The character identifier.

        **Returns:**
        - `bool`: True if a matching session exists, False otherwise.
        """
        sessions_dir = pathlib.Path(get_data_dir()) / "sessions"
        
        if not sessions_dir.exists() or not sessions_dir.is_dir():
            return False

        # Browse all session folders
        for session_folder in sessions_dir.iterdir():
            if session_folder.is_dir():
                try:
                    # Check for scenario.txt and character.txt files
                    scenario_file = session_folder / "scenario.txt"
                    character_file = session_folder / "character.txt"

                    if scenario_file.exists() and character_file.exists():
                        existing_scenario = scenario_file.read_text(encoding='utf-8').strip()
                        existing_character = character_file.read_text(encoding='utf-8').strip()

                        # Compare with provided parameters
                        if existing_scenario == scenario_name and existing_character == character_id:
                            log_debug("Existing session found", 
                                      action="check_existing_session", 
                                      session_id=session_folder.name, 
                                      scenario_name=scenario_name, 
                                      character_id=character_id)
                            return True

                except Exception:
                    # Ignore invalid folders or read errors
                    continue

        return False

    async def save_history(self, kind: str, messages: list) -> None:
        """
        ### save_history
        **Description:** Saves the message history for a specific mode (narrative or combat) to a JSONL file.

        **Parameters:**
        - `kind` (str): The type of history ("narrative" or "combat").
        - `messages` (list): A list of `ModelMessage` objects to save.
        
        **Returns:** None.
        """
        history_path = os.path.join(get_data_dir(), "sessions", self.session_id, f"history_{kind}.jsonl")
        store = PydanticJsonlStore(history_path)
        store.save_pydantic_history(messages)

    async def load_history(self, kind: str) -> List[ModelMessage]:
        """
        ### load_history
        **Description:** Loads the message history for a specific mode (narrative or combat) from a JSONL file.

        **Parameters:**
        - `kind` (str): The type of history ("narrative" or "combat").

        **Returns:**
        - `List[ModelMessage]`: A list of loaded `ModelMessage` objects. Returns an empty list if the file does not exist.
        """
        history_path = os.path.join(get_data_dir(), "sessions", self.session_id, f"history_{kind}.jsonl")
        if os.path.exists(history_path):
            store = PydanticJsonlStore(history_path)
            return store.load_pydantic_history()
        return []

    async def load_history_raw_json(self, kind: str) -> List[Dict[str, Any]]:
        """
        ### load_history_raw_json
        **Description:** Loads the message history for a specific mode as raw JSON dictionaries.
        Useful for API responses or debugging.

        **Parameters:**
        - `kind` (str): The type of history ("narrative" or "combat").

        **Returns:**
        - `List[Dict[str, Any]]`: A list of message dictionaries. Returns an empty list if the file does not exist.
        """
        history_path = os.path.join(get_data_dir(), "sessions", self.session_id, f"history_{kind}.jsonl")
        if os.path.exists(history_path):
            store = PydanticJsonlStore(history_path)
            return store.load_raw_json_history()
        return []

    async def update_game_state(self, game_state: Any) -> None:
        """
        ### update_game_state
        **Description:** Saves the current game state object to `game_state.json`.

        **Parameters:**
        - `game_state` (Any): The GameState object to save (must have a `model_dump` method).
        
        **Returns:** None.
        """
        import json
        state_path = os.path.join(get_data_dir(), "sessions", self.session_id, "game_state.json")
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(game_state.model_dump(), f, ensure_ascii=False, indent=2)

    async def load_game_state(self) -> Optional[Any]:
        """
        ### load_game_state
        **Description:** Loads the game state from `game_state.json`.

        **Returns:**
        - `Optional[GameState]`: The loaded GameState object, or None if the file does not exist.
        """
        from back.graph.dto.session import GameState
        import json
        state_path = os.path.join(get_data_dir(), "sessions", self.session_id, "game_state.json")
        if os.path.exists(state_path):
            with open(state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return GameState(**data)
        return None

    async def build_narrative_system_prompt(self) -> str:
        """
        ### build_narrative_system_prompt
        **Description:** Builds the system prompt for the narrative agent.
        Combines the scenario-specific prompt with the character's narrative information block.

        **Returns:**
        - `str`: The complete system prompt string.
        """
        # Use the full system prompt template
        prompt = build_system_prompt(self.scenario_id)

        # Build complete character information via Character method
        character_info = self.character_data.build_narrative_prompt_block() if self.character_data else "Unknown character"

        return prompt + f"\n\nCHARACTER INFORMATION:\n{character_info}"

    async def build_combat_prompt(self, combat_state: dict) -> str:
        """
        ### build_combat_prompt
        **Description:** Builds the system prompt for the combat agent.
        Includes the current combat state, character combat info, and available tools.

        **Parameters:**
        - `combat_state` (dict): The current state of the combat (participants, turns, etc.).

        **Returns:**
        - `str`: The complete system prompt string.
        """
        # Build complete character information for combat via Character method
        character_info = self.character_data.build_combat_prompt_block() if self.character_data else "Unknown character"

        return f"""
You are a Combat Master for a Middle-earth RPG.

Current Combat State:
{combat_state}

CHARACTER INFORMATION:
{character_info}

Resolve combat turns using the character's stats, skills, and equipment.
You have access to the following tools:
- roll_initiative_tool: Roll initiative for participants
- perform_attack_tool: Execute an attack roll
- resolve_attack_tool: Resolve attack vs defense
- calculate_damage_tool: Calculate damage with modifiers
- apply_damage_tool: Apply damage to a participant
- end_turn_tool: End the current turn
- check_combat_end_tool: Check if combat should end
- end_combat_tool: End the combat session
- get_combat_status_tool: Get current combat status
- skill_check_with_character: Perform skill checks
- inventory_remove_item: Remove items (e.g. ammunition)

Always consider the character's combat skills, equipment bonuses, and current HP when resolving actions.
"""