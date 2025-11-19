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
    **Description:** Service for managing game sessions, including message history,
    character data and scenario.
    **Attributes:**
    - `session_id` (str): Session identifier
    - `character_data` (Character): Character data for the session (typed object)
    - `scenario_id` (str): Scenario ID associated with the session
    - `data_service` (CharacterDataService): Data service for character
    - `character_service` (CharacterService): Character service
    - `equipment_service` (EquipmentService): Equipment service
    """

    def __init__(self, session_id: str, character_id: Optional[str] = None, scenario_id: Optional[str] = None):
        """
        ### __init__
        **Description:** Initialize the session service with an identifier.
        **Parameters:**
        - `session_id` (str): Unique session identifier
        - `character_id` (Optional[str]): Character ID for creating a new session
        - `scenario_id` (Optional[str]): Scenario ID for creating a new session
        """
        self.session_id = session_id
        self.character_id = character_id
        self.character_data: Optional[Character] = None
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

    def _load_session_data(self) -> bool:
        """
        ### _load_session_data
        **Description:** Load session data (character and scenario) from files.
        **Returns:** True if session exists, False otherwise.
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
                    if self.data_service:
                        self.character_data = self.data_service.load_character(character_id)
                    else:
                        raise ServiceNotInitializedError("Data service not initialized")
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

    def _create_session(self, character_id: str, scenario_id: str):
        """
        ### _create_session
        **Description:** Create a new session with character ID and scenario ID.
        **Parameters:**
        - `character_id` (str): Character ID
        - `scenario_id` (str): Scenario ID
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
            if self.data_service:
                self.character_data = self.data_service.load_character(character_id)
            else:
                raise ServiceNotInitializedError("Data service not initialized")
        except FileNotFoundError:
            raise CharacterNotFoundError(f"Character {character_id} not found")

        self.scenario_id = scenario_id

    def _initialize_services(self, character_id: str):
        """
        ### _initialize_services
        **Description:** Initialize specialized services for a given character.
        **Parameters:**
        - `character_id` (str): Character ID
        """
        # Data service
        self.data_service = CharacterDataService()

        # Character service
        self.character_service = CharacterService(character_id)

        # Equipment service (depends on data service)
        self.equipment_service = EquipmentService(self.data_service)

    def save_character(self) -> None:
        """
        ### save_character
        **Description:** Save the current character data.
        **Returns:** None
        """
        if self.character_data and self.data_service:
            self.data_service.save_character(self.character_data)

    @staticmethod
    def list_all_sessions() -> List[Dict[str, Any]]:
        """
        ### list_all_sessions
        **Description:** Retrieve the list of all sessions with scenario and character information.
        **Returns:** List of dictionaries containing information for each session
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
        Start a scenario with a specific character and create a unique session.

        Args:
            scenario_name (str): The name of the scenario to start.
            character_id (UUID): The character identifier.

        Returns:
            Dict[str, Any]: A dictionary containing session id, scenario name, character id, and confirmation message.

        Raises:
            ValueError: If a session already exists with the same scenario and character.
            FileNotFoundError: If the scenario does not exist.
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
        Retrieve session information (character_id and scenario_name) from its ID.

        Args:
            session_id (str): The session identifier.

        Returns:
            Dict[str, str]: A dictionary containing character_id and scenario_name.

        Raises:
            SessionNotFoundError: If the session does not exist.
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
        Check if a session already exists with the same scenario and character.

        Args:
            scenario_name (str): The scenario name.
            character_id (str): The character identifier.

        Returns:
            bool: True if a session already exists, False otherwise.
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

    # The following methods are removed as they are only used in tests:
    # - load_history
    # - save_history
    # - update_character_data

    async def save_history(self, kind: str, messages: list) -> None:
        """
        ### save_history
        **Description:** Save history messages for narrative or combat.
        **Parameters:**
        - `kind` (str): "narrative" or "combat"
        - `messages` (list): List of ModelMessage
        """
        history_path = os.path.join(get_data_dir(), "sessions", self.session_id, f"history_{kind}.jsonl")
        store = PydanticJsonlStore(history_path)
        store.save_pydantic_history(messages)

    async def load_history(self, kind: str) -> List[ModelMessage]:
        """
        ### load_history
        **Description:** Load history messages for narrative or combat.
        **Parameters:**
        - `kind` (str): "narrative" or "combat"
        **Returns:** List of ModelMessage
        """
        history_path = os.path.join(get_data_dir(), "sessions", self.session_id, f"history_{kind}.jsonl")
        if os.path.exists(history_path):
            store = PydanticJsonlStore(history_path)
            return store.load_pydantic_history()
        return []

    async def load_history_raw_json(self, kind: str) -> List[Dict[str, Any]]:
        """
        ### load_history_raw_json
        **Description:** Load history messages for narrative or combat as raw JSON.
        **Parameters:**
        - `kind` (str): "narrative" or "combat"
        **Returns:** List of raw JSON message dictionaries
        """
        history_path = os.path.join(get_data_dir(), "sessions", self.session_id, f"history_{kind}.jsonl")
        if os.path.exists(history_path):
            store = PydanticJsonlStore(history_path)
            return store.load_raw_json_history()
        return []

    async def update_game_state(self, game_state) -> None:
        """
        ### update_game_state
        **Description:** Save the game state to game_state.json.
        **Parameters:**
        - `game_state`: GameState instance
        """
        import json
        state_path = os.path.join(get_data_dir(), "sessions", self.session_id, "game_state.json")
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(game_state.model_dump(), f, ensure_ascii=False, indent=2)

    async def load_game_state(self):
        """
        ### load_game_state
        **Description:** Load the game state from game_state.json.
        **Returns:** GameState instance or None if not exists
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
        **Description:** Build the system prompt for narrative mode.
        **Returns:** System prompt string
        """
        # Use the full system prompt template
        prompt = build_system_prompt(self.scenario_id)

        # Build complete character information via Character method
        character_info = self.character_data.build_narrative_prompt_block() if self.character_data else "Unknown character"

        return prompt + f"\n\nCHARACTER INFORMATION:\n{character_info}"

    async def build_combat_prompt(self, combat_state: dict) -> str:
        """
        ### build_combat_prompt
        **Description:** Build the system prompt for combat mode.
        **Parameters:**
        - `combat_state` (dict): Current combat state
        **Returns:** System prompt string
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