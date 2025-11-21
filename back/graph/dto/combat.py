"""
DTOs for combat-related payloads and events.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from dataclasses import dataclass


class CombatantOutcome(BaseModel):
    """
    ### CombatantOutcome
    **Description:** Outcome for a combatant after a combat turn.
    **Attributes:**
    - `name` (str): Name of the combatant.
    - `hp_change` (int): Change in HP (positive for healing, negative for damage).
    - `status_effects` (List[str]): New status effects applied.
    - `is_dead` (bool): Whether the combatant is dead.
    """
    name: str
    hp_change: int = 0
    status_effects: List[str] = Field(default_factory=list)
    is_dead: bool = False


class DamageEvent(BaseModel):
    """
    ### DamageEvent
    **Description:** Event representing damage dealt.
    **Attributes:**
    - `attacker` (str): Name of the attacker.
    - `target` (str): Name of the target.
    - `damage` (int): Amount of damage dealt.
    - `damage_type` (str): Type of damage (e.g., "physical", "magical").
    """
    attacker: str
    target: str
    damage: int
    damage_type: str = "physical"


class HealingEvent(BaseModel):
    """
    ### HealingEvent
    **Description:** Event representing healing applied.
    **Attributes:**
    - `healer` (str): Name of the healer.
    - `target` (str): Name of the target.
    - `healing` (int): Amount of healing applied.
    """
    healer: str
    target: str
    healing: int


class InventoryEvent(BaseModel):
    """
    ### InventoryEvent
    **Description:** Event representing inventory changes.
    **Attributes:**
    - `character` (str): Name of the character.
    - `item` (str): Name of the item.
    - `action` (str): Action performed ("add", "remove", "equip").
    - `quantity` (int): Quantity changed.
    """
    character: str
    item: str
    action: str  # "add", "remove", "equip"
    quantity: int = 1


class XPEvent(BaseModel):
    """
    ### XPEvent
    **Description:** Event representing XP gain.
    **Attributes:**
    - `character` (str): Name of the character.
    - `xp_gained` (int): Amount of XP gained.
    """
    character: str
    xp_gained: int


@dataclass
class CombatSeedPayload:
    """
    ### CombatSeedPayload
    **Description:** Initial payload returned by start_combat_tool.
    Contains the ID of the created combat and a feedback message.
    The actual state is stored in the database/file system.
    
    **Attributes:**
    - `combat_id` (str): UUID of the created combat session.
    - `message` (str): Narrative feedback about the combat start.
    """
    combat_id: str
    message: str


class CombatTurnContinuePayload(BaseModel):
    """
    ### CombatTurnContinuePayload
    **Description:** Payload for continuing combat (turn processed, combat ongoing).
    **Attributes:**
    - `turn_summary` (str): Summary of the current turn.
    - `combatants_outcomes` (List[CombatantOutcome]): Outcomes for combatants.
    - `events` (List[DamageEvent | HealingEvent | InventoryEvent | XPEvent]): Events that occurred.
    """
    turn_summary: str
    combatants_outcomes: List[CombatantOutcome] = Field(default_factory=list)
    events: List[DamageEvent | HealingEvent | InventoryEvent | XPEvent] = Field(default_factory=list)


class CombatTurnEndPayload(BaseModel):
    """
    ### CombatTurnEndPayload
    **Description:** Payload for ending combat.
    **Attributes:**
    - `combat_summary` (str): Summary of the entire combat.
    - `winners` (List[str]): Names of the winning participants.
    - `combatants_outcomes` (List[CombatantOutcome]): Final outcomes for combatants.
    - `events` (List[DamageEvent | HealingEvent | InventoryEvent | XPEvent]): All events that occurred.
    """
    combat_summary: str
    winners: List[str]
    combatants_outcomes: List[CombatantOutcome] = Field(default_factory=list)
    events: List[DamageEvent | HealingEvent | InventoryEvent | XPEvent] = Field(default_factory=list)


class CombatResultPayload(BaseModel):
    """
    ### CombatResultPayload
    **Description:** Final result of a combat, stored in game_state.
    **Attributes:**
    - `combat_id` (str): Unique ID of the combat.
    - `summary` (str): Summary of the combat.
    - `winners` (List[str]): Winners of the combat.
    - `xp_awarded` (Dict[str, int]): XP awarded to characters.
    - `gold_awarded` (Dict[str, int]): Gold awarded to characters.
    """
    combat_id: str
    summary: str
    winners: List[str]
    xp_awarded: Dict[str, int] = Field(default_factory=dict)
    gold_awarded: Dict[str, int] = Field(default_factory=dict)