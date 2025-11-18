"""
Service for managing role-playing game sessions.
Handles loading and saving of history, as well as character and scenario data.
Refactored to use specialized services (Phase 3).
"""

import os
import pathlib
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4

from back.models.domain.character import Character
from back.services.character_data_service import CharacterDataService
from back.services.character_business_service import CharacterBusinessService
from back.services.equipment_service import EquipmentService
from back.storage.pydantic_jsonl_store import PydanticJsonlStore
from back.config import get_data_dir
from back.utils.logger import log_debug


class GameSessionService:
    """
    ### GameSessionService
    **Description:** Service for managing game sessions, including message history,
    character data and scenario.
    **Attributes:**
    - `session_id` (str): Session identifier
    - `character_data` (Character): Character data for the session (typed object)
    - `scenario_id` (str): Scenario ID associated with the session
    - `store` (PydanticJsonlStore): Store for message history
    - `data_service` (CharacterDataService): Data service for character
    - `business_service` (CharacterBusinessService): Business logic service
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
        self.business_service: Optional[CharacterBusinessService] = None
        self.equipment_service: Optional[EquipmentService] = None

        # Initialize the store for history
        if not os.path.isabs(session_id):
            history_path = os.path.join(get_data_dir(), "sessions", f"{session_id}.jsonl")
        else:
            history_path = session_id + ".jsonl"
        self.store = PydanticJsonlStore(history_path)

        # Load session data or create a new session
        if not self._load_session_data():
            # If session doesn't exist and parameters are provided, create a new session
            if character_id and scenario_id:
                self._create_session(character_id, scenario_id)
            else:
                raise ValueError(f"Session {session_id} does not exist and creation parameters are not provided")

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
                        raise ValueError("Data service not initialized")
                except FileNotFoundError:
                    raise ValueError(f"Character {character_id} not found")

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
                raise ValueError("Data service not initialized")
        except FileNotFoundError:
            raise ValueError(f"Character {character_id} not found")

        self.scenario_id = scenario_id

    def _initialize_services(self, character_id: str):
        """
        ### _initialize_services
        **Description:** Initialize specialized services for a given character.
        **Parameters:**
        - `character_id` (str): Character ID
        """
        # Data service
        self.data_service = CharacterDataService(character_id)

        # Business logic service (depends on data service)
        self.business_service = CharacterBusinessService(self.data_service)

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

    def apply_xp(self, xp: int) -> Character:
        """
        ### apply_xp
        **Description:** Apply XP to the character.
        **Parameters:**
        - `xp` (int): Experience points to add
        **Returns:** Modified character
        """
        if self.character_data and self.business_service:
            self.character_data = self.business_service.apply_xp(self.character_data, xp)
            return self.character_data
        raise ValueError("Services not initialized")

    def add_gold(self, gold: float) -> Character:
        """
        ### add_gold
        **Description:** Add gold to the character.
        **Parameters:**
        - `gold` (float): Amount of gold to add
        **Returns:** Modified character
        """
        if self.character_data and self.business_service:
            self.character_data = self.business_service.add_gold(self.character_data, gold)
            return self.character_data
        raise ValueError("Services not initialized")

    def take_damage(self, amount: int, source: str = "combat") -> Character:
        """
        ### take_damage
        **Description:** Apply damage to the character.
        **Parameters:**
        - `amount` (int): Damage points to apply
        - `source` (str): Damage source (optional)
        **Returns:** Modified character
        """
        if self.character_data and self.business_service:
            self.character_data = self.business_service.take_damage(self.character_data, amount, source)
            return self.character_data
        raise ValueError("Services not initialized")

    def add_item(self, item_id: str, quantity: int = 1) -> Character:
        """
        ### add_item
        **Description:** Add an item to the character's inventory.
        **Parameters:**
        - `item_id` (str): Item identifier
        - `quantity` (int): Quantity to add (default: 1)
        **Returns:** Modified character
        """
        if self.character_data and self.equipment_service:
            self.character_data = self.equipment_service.add_item(self.character_data, item_id, quantity)
            return self.character_data
        raise ValueError("Services not initialized")

    def remove_item(self, item_id: str, quantity: int = 1) -> Character:
        """
        ### remove_item
        **Description:** Remove an item from the character's inventory.
        **Parameters:**
        - `item_id` (str): Item identifier
        - `quantity` (int): Quantity to remove (default: 1)
        **Returns:** Modified character
        """
        if self.character_data and self.equipment_service:
            self.character_data = self.equipment_service.remove_item(self.character_data, item_id, quantity)
            return self.character_data
        raise ValueError("Services not initialized")

    def buy_equipment(self, equipment_name: str) -> Character:
        """
        ### buy_equipment
        **Description:** Buy equipment for the character.
        **Parameters:**
        - `equipment_name` (str): Equipment name
        **Returns:** Modified character
        """
        if self.character_data and self.equipment_service:
            self.character_data = self.equipment_service.buy_equipment(self.character_data, equipment_name)
            return self.character_data
        raise ValueError("Services not initialized")

    def sell_equipment(self, equipment_name: str) -> Character:
        """
        ### sell_equipment
        **Description:** Sell equipment from the character.
        **Parameters:**
        - `equipment_name` (str): Equipment name
        **Returns:** Modified character
        """
        if self.character_data and self.equipment_service:
            self.character_data = self.equipment_service.sell_equipment(self.character_data, equipment_name)
            return self.character_data
        raise ValueError("Services not initialized")

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
            FileNotFoundError: If the session does not exist.
        """
        session_dir = pathlib.Path(get_data_dir()) / "sessions" / session_id

        if not session_dir.exists() or not session_dir.is_dir():
            raise FileNotFoundError(f"The session '{session_id}' does not exist.")

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