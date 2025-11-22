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
from back.models.enums import CharacterStatus
from back.services.character_data_service import CharacterDataService
from back.services.character_service import CharacterService
from back.dependencies import global_container
from back.services.equipment_service import EquipmentService
from back.storage.pydantic_jsonl_store import PydanticJsonlStore
from back.config import get_data_dir
from back.utils.logger import log_debug, log_warning
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

    def __init__(self, session_id: str) -> None:
        """
        ### __init__
        **Description:** Initializes the session service with a session identifier.
        **Note:** Does NOT load data automatically. Use `create` or `load` factory methods.

        **Parameters:**
        - `session_id` (str): Unique session identifier.
        """
        self.session_id = session_id
        self.character_id: Optional[str] = None
        self.scenario_id: str = ""

        # Specialized services
        self.data_service: Optional[CharacterDataService] = None
        self.character_service: Optional[CharacterService] = None
        self.equipment_service: Optional[EquipmentService] = None
        self._combat_system_prompt: Optional[str] = None

    @classmethod
    async def create(cls, session_id: str, character_id: str, scenario_id: str) -> 'GameSessionService':
        """
        ### create
        **Description:** Async factory to create a new session.
        
        **Parameters:**
        - `session_id` (str): Unique session identifier.
        - `character_id` (str): Character ID.
        - `scenario_id` (str): Scenario ID.
        
        **Returns:**
        - `GameSessionService`: Initialized service instance.
        """
        instance = cls(session_id)
        await instance._create_session(character_id, scenario_id)
        return instance

    @classmethod
    async def load(cls, session_id: str) -> 'GameSessionService':
        """
        ### load
        **Description:** Async factory to load an existing session.
        
        **Parameters:**
        - `session_id` (str): Unique session identifier.
        
        **Returns:**
        - `GameSessionService`: Initialized service instance.
        
        **Raises:**
        - `SessionNotFoundError`: If session does not exist.
        """
        instance = cls(session_id)
        if not await instance._load_session_data():
             raise SessionNotFoundError(f"Session {session_id} does not exist")
        return instance

    async def _load_session_data(self) -> bool:
        """
        ### _load_session_data
        **Description:** Asynchronously loads session metadata.
        """
        import aiofiles
        session_dir = pathlib.Path(get_data_dir()) / "sessions" / self.session_id
        if session_dir.exists() and session_dir.is_dir():
            # Load character ID
            character_file = session_dir / "character.txt"
            if character_file.exists():
                async with aiofiles.open(character_file, mode='r', encoding='utf-8') as f:
                    content = await f.read()
                    self.character_id = content.strip()

                # Initialize specialized services for this character
                try:
                    self._initialize_services()
                except FileNotFoundError:
                    raise CharacterNotFoundError(f"Character {self.character_id} not found")

            # Load scenario ID
            scenario_file = session_dir / "scenario.txt"
            if scenario_file.exists():
                async with aiofiles.open(scenario_file, mode='r', encoding='utf-8') as f:
                    content = await f.read()
                    self.scenario_id = content.strip()
            else:
                raise ValueError(f"Missing scenario.txt file for session '{self.session_id}'.")

            return True

        return False

    async def _create_session(self, character_id: str, scenario_id: str) -> None:
        """
        ### _create_session
        **Description:** Asynchronously creates a new session directory and saves metadata.
        """
        import aiofiles
        session_dir = pathlib.Path(get_data_dir()) / "sessions" / self.session_id

        # Create session directory (sync operation, but fast/rare)
        session_dir.mkdir(parents=True, exist_ok=True)

        # Save character ID
        character_file = session_dir / "character.txt"
        async with aiofiles.open(character_file, mode='w', encoding='utf-8') as f:
            await f.write(character_id)

        # Save scenario ID
        scenario_file = session_dir / "scenario.txt"
        async with aiofiles.open(scenario_file, mode='w', encoding='utf-8') as f:
            await f.write(scenario_id)

        # Set character_id attribute
        self.character_id = character_id

        # Initialize specialized services for this character
        try:
            self._initialize_services()
        except FileNotFoundError:
            raise CharacterNotFoundError(f"Character {character_id} not found")

        self.scenario_id = scenario_id

    def _initialize_services(self) -> None:
        """
        ### _initialize_services
        **Description:** Initializes internal services using the DependencyContainer.
        Retrieves singleton instances for stateless services and creates a new
        CharacterService (stateful) injected with the singleton data service.
        """
        # 1. Get Singletons from Container
        self.data_service = global_container.character_data_service
        self.equipment_service = global_container.equipment_service
        
        # 2. Initialize CharacterService (Stateful - per session)
        # We inject the singleton data_service into it
        try:
            self.character_service = CharacterService(
                str(self.character_id), 
                data_service=self.data_service
            )
        except Exception as e:
            log_warning(f"Failed to initialize CharacterService: {e}", session_id=self.session_id)
            self.character_service = None

    @staticmethod
    async def list_all_sessions() -> List[Dict[str, Any]]:
        """
        ### list_all_sessions
        **Description:** Asynchronously retrieves a list of all available game sessions with their metadata.

        **Returns:** 
        - `List[Dict[str, Any]]`: A list of dictionaries containing `session_id`, `character_id`, and `scenario_id` for each session.
        """
        import aiofiles
        sessions_dir = pathlib.Path(get_data_dir()) / "sessions"
        
        all_sessions = []

        if sessions_dir.exists() and sessions_dir.is_dir():
            # iterdir is sync, but directory listing is usually fast. 
            # For strict async, we could use run_in_executor, but it might be overkill here.
            # We will make the file reading async.
            for session_path in sessions_dir.iterdir():
                if session_path.is_dir():
                    # Load character ID
                    character_file = session_path / "character.txt"
                    if character_file.exists():
                        async with aiofiles.open(character_file, mode='r', encoding='utf-8') as f:
                            content = await f.read()
                            character_id = content.strip()
                    else:
                        character_id = "Unknown"

                    # Load scenario ID
                    scenario_file = session_path / "scenario.txt"
                    if scenario_file.exists():
                        async with aiofiles.open(scenario_file, mode='r', encoding='utf-8') as f:
                            content = await f.read()
                            scenario_id = content.strip()
                    else:
                        scenario_id = "Unknown"

                    all_sessions.append({
                        "session_id": session_path.name,
                        "character_id": character_id,
                        "scenario_id": scenario_id
                    })

        return all_sessions

    @staticmethod
    async def start_scenario(scenario_name: str, character_id: UUID) -> Dict[str, Any]:
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
        import aiofiles
        # Check if a session already exists with the same scenario and character
        if await GameSessionService.check_existing_session(scenario_name, str(character_id)):
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
        async with aiofiles.open(character_file, mode='w', encoding='utf-8') as f:
            await f.write(str(character_id))

        # Store the scenario name in the session
        scenario_file = session_dir / "scenario.txt"
        async with aiofiles.open(scenario_file, mode='w', encoding='utf-8') as f:
            await f.write(scenario_name)

        # Update character status to IN_GAME
        try:
            char_service = CharacterService(str(character_id))
            char_service.character_data.status = CharacterStatus.IN_GAME
            char_service.save_character()
            log_debug(f"Character {character_id} status updated to IN_GAME")
        except Exception as e:
            log_debug(f"Failed to update character status to IN_GAME: {e}")
            # Non-blocking error, we continue


        log_debug("Scenario started", action="start_scenario", session_id=session_id, character_id=str(character_id), scenario_name=scenario_name)
        return {
            "session_id": session_id,
            "scenario_name": scenario_name,
            "character_id": str(character_id),
            "message": f"Scenario '{scenario_name}' successfully started for character {character_id}."
        }



    @staticmethod
    async def get_session_info(session_id: str) -> Dict[str, str]:
        """
        ### get_session_info
        **Description:** Asynchronously retrieves metadata (character ID and scenario name) for a given session ID.

        **Parameters:**
        - `session_id` (str): The unique session identifier.

        **Returns:**
        - `Dict[str, str]`: A dictionary containing `character_id` and `scenario_name`.

        **Raises:**
        - `SessionNotFoundError`: If the session directory does not exist.
        - `FileNotFoundError`: If metadata files are missing within the session directory.
        """
        import aiofiles
        session_dir = pathlib.Path(get_data_dir()) / "sessions" / session_id

        if not session_dir.exists() or not session_dir.is_dir():
            raise SessionNotFoundError(f"The session '{session_id}' does not exist.")

        # Retrieve the character ID
        character_file = session_dir / "character.txt"
        if not character_file.exists():
            raise FileNotFoundError(f"Missing character.txt file for session '{session_id}'.")

        async with aiofiles.open(character_file, mode='r', encoding='utf-8') as f:
            content = await f.read()
            character_id = content.strip()

        # Retrieve the scenario name
        scenario_file = session_dir / "scenario.txt"
        if not scenario_file.exists():
            raise FileNotFoundError(f"Missing scenario.txt file for session '{session_id}'.")

        async with aiofiles.open(scenario_file, mode='r', encoding='utf-8') as f:
            content = await f.read()
            scenario_name = content.strip()

        log_debug("Session information retrieved", action="get_session_info", session_id=session_id, character_id=character_id, scenario_name=scenario_name)
        return {
            "character_id": character_id,
            "scenario_name": scenario_name
        }

    @staticmethod
    async def check_existing_session(scenario_name: str, character_id: str) -> bool:
        """
        ### check_existing_session
        **Description:** Asynchronously checks if a session already exists for a specific combination of scenario and character.

        **Parameters:**
        - `scenario_name` (str): The name of the scenario.
        - `character_id` (str): The character identifier.

        **Returns:**
        - `bool`: True if a matching session exists, False otherwise.
        """
        import aiofiles
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
                        async with aiofiles.open(scenario_file, mode='r', encoding='utf-8') as f:
                            content = await f.read()
                            existing_scenario = content.strip()
                        
                        async with aiofiles.open(character_file, mode='r', encoding='utf-8') as f:
                            content = await f.read()
                            existing_character = content.strip()

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
        await store.save_pydantic_history_async(messages)

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
            return await store.load_pydantic_history_async()
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
            return await store.load_raw_json_history_async()
        return []

    async def save_history_llm(self, kind: str, messages: list) -> None:
        """
        ### save_history_llm
        **Description:** Saves the summarized message history for LLM context.
        This history is separate from the full UI history.

        **Parameters:**
        - `kind` (str): The type of history ("narrative" or "combat").
        - `messages` (list): A list of `ModelMessage` objects to save.
        """
        history_path = os.path.join(get_data_dir(), "sessions", self.session_id, f"history_{kind}_llm.jsonl")
        store = PydanticJsonlStore(history_path)
        await store.save_pydantic_history_async(messages)

    async def load_history_llm(self, kind: str) -> List[ModelMessage]:
        """
        ### load_history_llm
        **Description:** Loads the summarized message history for LLM context.

        **Parameters:**
        - `kind` (str): The type of history ("narrative" or "combat").

        **Returns:**
        - `List[ModelMessage]`: A list of loaded `ModelMessage` objects.
        """
        history_path = os.path.join(get_data_dir(), "sessions", self.session_id, f"history_{kind}_llm.jsonl")
        if os.path.exists(history_path):
            store = PydanticJsonlStore(history_path)
            return await store.load_pydantic_history_async()
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
        import aiofiles
        state_path = os.path.join(get_data_dir(), "sessions", self.session_id, "game_state.json")
        async with aiofiles.open(state_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(game_state.model_dump(), ensure_ascii=False, indent=2))

    async def load_game_state(self) -> Optional[Any]:
        """
        ### load_game_state
        **Description:** Loads the game state from `game_state.json`.

        **Returns:**
        - `Optional[GameState]`: The loaded GameState object, or None if the file does not exist.
        """
        from back.graph.dto.session import GameState
        import json
        import aiofiles
        state_path = os.path.join(get_data_dir(), "sessions", self.session_id, "game_state.json")
        if os.path.exists(state_path):
            async with aiofiles.open(state_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
            return GameState(**data)
        return None

    async def build_narrative_system_prompt(self, language: str = "English") -> str:
        """
        ### build_narrative_system_prompt
        **Description:** Builds the system prompt for the narrative agent.
        Combines the scenario-specific prompt with the character's narrative information block.

        **Parameters:**
        - `language` (str): The language for the interaction.

        **Returns:**
        - `str`: The complete system prompt string.
        """
        # Use the full system prompt template
        prompt = build_system_prompt(self.scenario_id, language)

        # Build complete character information via Character method
        character_info = "Unknown character"
        if self.character_service and self.character_service.character_data:
            character_info = self.character_service.character_data.build_narrative_prompt_block()

        return prompt + f"\n\nCHARACTER INFORMATION:\n{character_info}"

    async def build_combat_prompt(self, combat_state: Any, language: str = "English") -> str:
        """
        ### build_combat_prompt
        **Description:** Builds the system prompt for the combat agent.
        Includes the current combat state, character combat info, and available tools.

        **Parameters:**
        - `combat_state` (Any): The current state of the combat (CombatState object or dict).
        - `language` (str): The language for the interaction.

        **Returns:**
        - `str`: The complete system prompt string.
        """
        # Build complete character information for combat via Character method
        character_info = "Unknown character"
        if self.character_service and self.character_service.character_data:
            character_info = self.character_service.character_data.build_combat_prompt_block()

        # Format combat state if it's an object
        state_summary = combat_state
        if hasattr(combat_state, 'model_dump'):
             # It's a Pydantic model (CombatState)
             # We can use a summary method if available, or dump it
             # Ideally we use the service's summary method, but here we might just dump it
             # or rely on the __str__ or similar.
             # Let's use model_dump for now, or better, just pass it and let str() handle it if it's a dict
             state_summary = combat_state.model_dump()

        return f"""
You are a Combat Master for a Middle-earth RPG.
Language: {language}

Current Combat State:
{state_summary}

CHARACTER INFORMATION:
{character_info}

YOUR ROLE:
- You are the Game Master handling the combat logic.
- You MUST make high-level decisions based on the player's intent and the combat state.
- Do NOT ask the player to roll dice. YOU decide the outcome using the provided tools.
- Describe the action dynamically and immersively.

TOOLS USAGE:
- execute_attack_tool: Use this for ANY physical attack (melee or ranged). It handles the roll, AC check, and damage automatically.
- apply_direct_damage_tool: Use this for spells, traps, or environmental damage that does NOT require an attack roll (e.g., "Fireball" save, falling damage).
- end_turn_tool: MANDATORY at the end of the active participant's turn.
- check_combat_end_tool: Use this after every action that might end the combat.
- end_combat_tool: Use this to force end the combat (e.g., surrender, escape).
- get_combat_status_tool: Use this if you need to refresh the state.
- skill_check_with_character: Use this for non-combat actions (e.g., Acrobatics to jump on a table).
- inventory_remove_item: Use this to remove items (sold/lost).
- inventory_decrease_quantity: Use this to consume ammo (arrows) or supplies (potions).

TURN FLOW:
1. Analyze the current turn owner (Player or NPC).
2. If NPC: Decide their action, execute it using tools, describe the result, and END TURN.
3. If Player: Interpret their message.
   - If they attack: Call `execute_attack_tool`.
   - If they cast a spell (damage): Call `apply_direct_damage_tool` (after checking logic/saves if needed).
   - If they do something else: Resolve it.
   - AFTER the action, call `check_combat_end_tool`.
   - If combat continues, call `end_turn_tool`.
4. ALWAYS describe the outcome of the tools (hit/miss, damage) in the narrative.

IMPORTANT:
- `execute_attack_tool` requires `attacker_id` and `target_id`.
- Do NOT hallucinate weapon names or damage dice; the tool handles it.
"""