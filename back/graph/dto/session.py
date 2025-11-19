"""
DTOs for session graph state management.
"""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field
from pydantic_ai.messages import ModelMessage
from dataclasses import dataclass


class GameState(BaseModel):
    """
    ### GameState
    **Description:** Persistent state of the game session stored in game_state.json.
    **Attributes:**
    - `session_mode` (Literal["narrative", "combat"]): Current mode of the session.
    - `narrative_history_id` (str): ID for narrative history file.
    - `combat_history_id` (str): ID for combat history file.
    - `combat_state` (dict[str, Any] | None): Snapshot of active combat state.
    - `last_combat_result` (dict[str, Any] | None): Result of the last combat.
    """
    session_mode: Literal["narrative", "combat"] = "narrative"
    narrative_history_id: str = "default"
    combat_history_id: str = "default"
    combat_state: Optional[dict[str, Any]] = None
    last_combat_result: Optional[dict[str, Any]] = None


@dataclass
class PlayerMessagePayload:
    """
    ### PlayerMessagePayload
    **Description:** Payload containing the player's message for the current turn.
    **Attributes:**
    - `message` (str): The player's input message.
    """
    message: str


@dataclass
class DispatchResult:
    """
    ### DispatchResult
    **Description:** Result of dispatching a graph run, containing serialized messages.
    **Attributes:**
    - `all_messages` (list[dict[str, Any]]): Complete message history as JSON-serializable dicts.
    - `new_messages` (list[dict[str, Any]]): New messages from this turn as JSON-serializable dicts.
    """
    all_messages: list[dict[str, Any]]
    new_messages: list[dict[str, Any]]


@dataclass
class SessionGraphState:
    """
    ### SessionGraphState
    **Description:** State passed to each graph node via ctx.state.
    **Attributes:**
    - `game_state` (GameState): Persistent game state loaded from game_state.json.
    - `pending_player_message` (PlayerMessagePayload): Current player message.
    - `model_messages` (list[ModelMessage] | None): Buffer of history messages loaded by dispatcher.
    - `active_history_kind` (Literal["narrative", "combat"] | None): Type of history currently loaded.
    """
    game_state: GameState
    pending_player_message: PlayerMessagePayload
    model_messages: Optional[list[ModelMessage]] = None
    active_history_kind: Optional[Literal["narrative", "combat"]] = None